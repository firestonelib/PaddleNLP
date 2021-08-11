import os
import yaml
import argparse
from pprint import pprint
from attrdict import AttrDict

import paddle
from paddlenlp.transformers import TransformerModel, position_encoding_init
import reader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="./configs/transformer.base.yaml",
        type=str,
        help="Path of the config file. ")
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Whether to print logs on each cards and use benchmark vocab. Normally, not necessary to set --benchmark. "
    )
    parser.add_argument(
        "--test_file",
        default=None,
        type=str,
        help="The file for testing. Normally, it shouldn't be set and in this case, the default WMT14 dataset will be used to process testing."
    )
    args = parser.parse_args()
    return args


def post_process_seq(seq, bos_idx, eos_idx, output_bos=False, output_eos=False):
    """
    Post-process the decoded sequence.
    """
    eos_pos = len(seq) - 1
    for i, idx in enumerate(seq):
        if idx == eos_idx:
            eos_pos = i
            break
    seq = [
        idx for idx in seq[:eos_pos + 1]
        if (output_bos or idx != bos_idx) and (output_eos or idx != eos_idx)
    ]
    return seq


def do_predict(args):
    if args.device == "gpu":
        place = "gpu"
    else:
        place = "cpu"

    paddle.set_device(place)

    # Define data loader
    test_loader, to_tokens = reader.create_infer_loader(args)

    # Define model
    transformer = TransformerModel(
        src_vocab_size=args.src_vocab_size,
        trg_vocab_size=args.trg_vocab_size,
        max_length=args.max_length + 1,
        num_encoder_layers=args.n_layer,
        num_decoder_layers=args.n_layer,
        n_head=args.n_head,
        d_model=args.d_model,
        d_inner_hid=args.d_inner_hid,
        dropout=args.dropout,
        weight_sharing=args.weight_sharing,
        bos_id=args.bos_idx,
        eos_id=args.eos_idx)

    # Load the trained model
    assert args.init_from_params, (
        "Please set init_from_params to load the infer model.")
    model_dict = paddle.load(
        os.path.join(args.init_from_params, "transformer.pdparams"))

    # To avoid a longer length than training, reset the size of position
    # encoding to max_length
    model_dict["src_pos_embedding.pos_encoder.weight"] = position_encoding_init(
        args.max_length + 1, args.d_model)
    model_dict["trg_pos_embedding.pos_encoder.weight"] = position_encoding_init(
        args.max_length + 1, args.d_model)

    # Load the model_dict
    transformer.load_dict(model_dict)

    # Set evaluate mode
    transformer.eval()

    f = open(args.output_file, "w", encoding="utf-8")

    with paddle.no_grad():
        for (src_word, ) in test_loader:
            finished_seq, finished_scores = transformer.beam_search_v2(
                src_word=src_word,
                beam_size=args.beam_size,
                max_len=args.max_out_len,
                alpha=0.6)
            finished_seq = finished_seq.numpy()
            for ins in finished_seq:
                for beam_idx, beam in enumerate(ins):
                    if beam_idx >= args.n_best:
                        break
                    id_list = post_process_seq(beam, args.bos_idx, args.eos_idx)
                    word_list = to_tokens(id_list)
                    sequence = " ".join(word_list) + "\n"
                    f.write(sequence)
    f.close()


if __name__ == "__main__":
    ARGS = parse_args()
    yaml_file = ARGS.config
    with open(yaml_file, 'rt') as f:
        args = AttrDict(yaml.safe_load(f))
    args.benchmark = ARGS.benchmark
    args.test_file = ARGS.test_file
    pprint(args)

    do_predict(args)
