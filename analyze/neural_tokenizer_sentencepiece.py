import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input="dataset.txt",
    model_prefix="adaptive_tokenizer",
    vocab_size=85,
    model_type="unigram"
)

sp = spm.SentencePieceProcessor(model_file="adaptive_tokenizer.model")
print(sp.encode_as_pieces("Adaptive tokenization improves efficiency."))



# Output:
# (myenv) root@localhost:~/analyze# python neural_tokenizer_sentencepiece.py
# sentencepiece_trainer.cc(78) LOG(INFO) Starts training with :
# trainer_spec {
#   input: dataset.txt
#   input_format:
#   model_prefix: adaptive_tokenizer
#   model_type: UNIGRAM
#   vocab_size: 85
#   self_test_sample_size: 0
#   character_coverage: 0.9995
#   input_sentence_size: 0
#   shuffle_input_sentence: 1
#   seed_sentencepiece_size: 1000000
#   shrinking_factor: 0.75
#   max_sentence_length: 4192
#   num_threads: 16
#   num_sub_iterations: 2
#   max_sentencepiece_length: 16
#   split_by_unicode_script: 1
#   split_by_number: 1
#   split_by_whitespace: 1
#   split_digits: 0
#   pretokenization_delimiter:
#   treat_whitespace_as_suffix: 0
#   allow_whitespace_only_pieces: 0
#   required_chars:
#   byte_fallback: 0
#   vocabulary_output_piece_score: 1
#   train_extremely_large_corpus: 0
#   seed_sentencepieces_file:
#   hard_vocab_limit: 1
#   use_all_vocab: 0
#   unk_id: 0
#   bos_id: 1
#   eos_id: 2
#   pad_id: -1
#   unk_piece: <unk>
#   bos_piece: <s>
#   eos_piece: </s>
#   pad_piece: <pad>
#   unk_surface:  ⁇
#   enable_differential_privacy: 0
#   differential_privacy_noise_level: 0
#   differential_privacy_clipping_threshold: 0
# }
# normalizer_spec {
#   name: nmt_nfkc
#   add_dummy_prefix: 1
#   remove_extra_whitespaces: 1
#   escape_whitespaces: 1
#   normalization_rule_tsv:
# }
# denormalizer_spec {}
# trainer_interface.cc(353) LOG(INFO) SentenceIterator is not specified. Using MultiFileSentenceIterator.
# trainer_interface.cc(185) LOG(INFO) Loading corpus: dataset.txt
# trainer_interface.cc(409) LOG(INFO) Loaded all 9 sentences
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: <unk>
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: <s>
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: </s>
# trainer_interface.cc(430) LOG(INFO) Normalizing sentences...
# trainer_interface.cc(539) LOG(INFO) all chars count=410
# trainer_interface.cc(560) LOG(INFO) Alphabet size=38
# trainer_interface.cc(561) LOG(INFO) Final character coverage=1
# trainer_interface.cc(592) LOG(INFO) Done! preprocessed 9 sentences.
# unigram_model_trainer.cc(265) LOG(INFO) Making suffix array...
# unigram_model_trainer.cc(269) LOG(INFO) Extracting frequent sub strings... node_num=201
# unigram_model_trainer.cc(312) LOG(INFO) Initialized 117 seed sentencepieces
# trainer_interface.cc(598) LOG(INFO) Tokenizing input sentences with whitespace: 9
# trainer_interface.cc(609) LOG(INFO) Done! 47
# unigram_model_trainer.cc(602) LOG(INFO) Using 47 sentences for EM training
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=0 size=83 obj=17.7537 num_tokens=195 num_tokens/piece=2.3494
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=1 size=79 obj=15.9392 num_tokens=196 num_tokens/piece=2.48101
# trainer_interface.cc(687) LOG(INFO) Saving model: adaptive_tokenizer.model
# trainer_interface.cc(699) LOG(INFO) Saving vocabs: adaptive_tokenizer.vocab
# ['▁', 'A', 'd', 'a', 'p', 't', 'i', 'v', 'e', '▁tokeniz', 'at', 'i', 'o', 'n', '▁i', 'm', 'p', 'r', 'o', 'v', 'e', 's', '▁', 'e', 'f', 'f', 'i', 'c', 'i', 'enc', 'y', '.']