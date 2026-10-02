"""SHOT target adaptation (Liang, Hu & Feng, ICML 2020) patched into SDALR's target script (PROTOCOL C85).

Replaces SDALR's `obtain_label` and `train_target` with SHOT's, keeping SDALR's backbone, source models, data loaders, logging
format, epochs, batch size and learning rate. Faithful to SHOT:
  * the source classifier head (networks[-1]) is frozen;
  * loss = beta * CE(pseudo-labels) + L_ent - L_div  (information maximisation), beta = 0.3;
  * pseudo-labels from weighted centroids in the (L2-normalised, bias-augmented) feature space, cosine distance, then one
    refinement with hard assignments; recomputed at the start of every epoch;
  * no reliability filtering, no mix-up, no auxiliary losses; the LAST iterate is evaluated (no checkpoint selection).
"""

SHOT_CODE = r'''
def obtain_label(loader, networks, args):
    start_test = True
    with torch.no_grad():
        for data in loader:
            inputs = data[0].cuda(); labels = data[1]
            feas = inputs
            for net in networks[:-1]:
                feas = net(feas)
            outputs = networks[-1](feas)
            if start_test:
                all_fea = feas.float().cpu(); all_output = outputs.float().cpu(); all_label = labels.float(); start_test = False
            else:
                all_fea = torch.cat((all_fea, feas.float().cpu()), 0)
                all_output = torch.cat((all_output, outputs.float().cpu()), 0)
                all_label = torch.cat((all_label, labels.float()), 0)
    all_output = nn.Softmax(dim=1)(all_output)
    _, predict = torch.max(all_output, 1)
    all_fea = torch.cat((all_fea, torch.ones(all_fea.size(0), 1)), 1)
    all_fea = (all_fea.t() / torch.norm(all_fea, p=2, dim=1)).t().numpy()
    K = all_output.size(1)
    aff = all_output.numpy()
    initc = aff.transpose().dot(all_fea) / (1e-8 + aff.sum(axis=0)[:, None])
    dd = cdist(all_fea, initc, 'cosine')
    pred_label = dd.argmin(axis=1)
    for _ in range(1):
        aff = np.eye(K)[pred_label]
        initc = aff.transpose().dot(all_fea) / (1e-8 + aff.sum(axis=0)[:, None])
        dd = cdist(all_fea, initc, 'cosine')
        pred_label = dd.argmin(axis=1)
    acc_before = float(np.mean(predict.numpy() == all_label.numpy()))
    acc_after = float(np.mean(pred_label == all_label.numpy()))
    log_str = f'SHOT pseudo-labels: model {acc_before * 100:.2f}% -> centroid {acc_after * 100:.2f}%'
    args.out_file.write(log_str + '\n'); args.out_file.flush(); print(log_str)
    return pred_label.astype('int')


def train_target(args, dset_loaders, networks):
    param_group = []
    for idx, net in enumerate(networks):
        for k, v in net.named_parameters():
            if idx == len(networks) - 1:
                v.requires_grad = False          # SHOT: frozen source hypothesis (classifier head)
            else:
                param_group += [{'params': v, 'lr': args.lr * args.lr_f[idx]}]
    optimizer = optim.SGD(param_group)
    optimizer = op_copy(optimizer)
    max_iter = args.max_epoch * len(dset_loaders["train"])
    iter_num = 0
    start = time.time()
    for net in networks:
        net.eval()
    acc_t_te, acc_matrix, _ = tools.cal_acc(dset_loaders["val"], networks)
    log_str = "任务: {}; 批次:{:·>5d}/{:·>5d};  总正确率: {:4.2f}%".format(args.name, iter_num, max_iter, acc_t_te) + "\n"
    log_str += tools.print_acc(acc_matrix)[1]
    args.out_file.write(log_str + "\n"); args.out_file.flush(); print(log_str + "\n")
    epoch_len = len(dset_loaders["train"])
    while iter_num < max_iter:
        if iter_num % epoch_len == 0:
            for net in networks:
                net.eval()
            mem_label = torch.from_numpy(obtain_label(dset_loaders["train"], networks, args)).cuda()
            for net in networks:
                net.train()
            networks[-1].eval()
            iter_test = iter(dset_loaders["train"])
        try:
            inputs_test, _, tar_idx = next(iter_test)
        except StopIteration:
            iter_test = iter(dset_loaders["train"]); inputs_test, _, tar_idx = next(iter_test)
        if inputs_test.size(0) == 1:
            continue
        inputs_test = inputs_test.cuda()
        iter_num += 1
        lr_scheduler(optimizer, iter_num=iter_num, max_iter=max_iter)
        feas = inputs_test
        for net in networks[:-1]:
            feas = net(feas)
        outputs_test = networks[-1](feas)
        pred = mem_label[tar_idx]
        classifier_loss = nn.CrossEntropyLoss()(outputs_test, pred) * args.shot_cls_par
        softmax_out = nn.Softmax(dim=1)(outputs_test)
        entropy_loss = torch.mean(loss.Entropy(softmax_out))
        msoftmax = softmax_out.mean(dim=0)
        gentropy_loss = torch.sum(-msoftmax * torch.log(msoftmax + args.epsilon))
        im_loss = entropy_loss - gentropy_loss
        total = classifier_loss + im_loss
        optimizer.zero_grad(); total.backward(); optimizer.step()
        if iter_num % epoch_len == 0:
            print("轮次:{:·>3d}/{:·>3d} || cls:{:4.3f} || im:{:4.3f} || 耗时：{:4.2f}s".format(
                iter_num // epoch_len, args.max_epoch, float(classifier_loss), float(im_loss), time.time() - start))
            start = time.time()
    for net in networks:
        net.eval()
    acc_t_te, acc_matrix, _ = tools.cal_acc(dset_loaders["test"], networks)
    log_str = '测试集任务: {}; 总正确率 = {:4.2f}%'.format(args.name, acc_t_te) + '\n'
    correct_rate, acc_str = tools.print_acc(acc_matrix)
    log_str += acc_str
    args.out_file.write(log_str + '\n'); args.out_file.flush(); print(log_str + '\n')
    args.class_acc_list = [np.mean(correct_rate)] + correct_rate
    args.acc_list[args.find_k(args.s, args.t)] = acc_t_te
    for net in networks:
        net.train()
    return networks


'''


def patch(source: str) -> str:
    i = source.index("def obtain_label(")
    j = source.index('if __name__ == "__main__":')
    patched = source[:i] + SHOT_CODE + source[j:]
    anchor = "    parser.add_argument('--mix', type=float, default=0)"
    if anchor not in patched:
        raise SystemExit("REFUSED: SHOT patch anchor not found in the SDALR target script")
    return patched.replace(anchor, anchor + "\n    parser.add_argument('--shot_cls_par', type=float, default=0.3)", 1)
