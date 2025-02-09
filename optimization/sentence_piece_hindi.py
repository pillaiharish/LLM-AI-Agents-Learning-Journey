import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input="hindi_dataset.txt",
    model_prefix="hindi_tokenizer",
    vocab_size=100
)

sp = spm.SentencePieceProcessor(model_file="hindi_tokenizer.model")
print(sp.encode_as_pieces("मशीन लर्निंग महत्वपूर्ण है।"))


# (myenv) harish:optimization $ python sentence_piece_hindi.py 
# sentencepiece_trainer.cc(78) LOG(INFO) Starts training with : 
# trainer_spec {
#   input: hindi_dataset.txt
#   input_format: 
#   model_prefix: hindi_tokenizer
#   model_type: UNIGRAM
#   vocab_size: 100
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
# trainer_interface.cc(185) LOG(INFO) Loading corpus: hindi_dataset.txt
# trainer_interface.cc(409) LOG(INFO) Loaded all 91 sentences
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: <unk>
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: <s>
# trainer_interface.cc(425) LOG(INFO) Adding meta_piece: </s>
# trainer_interface.cc(430) LOG(INFO) Normalizing sentences...
# trainer_interface.cc(539) LOG(INFO) all chars count=1897
# trainer_interface.cc(560) LOG(INFO) Alphabet size=55
# trainer_interface.cc(561) LOG(INFO) Final character coverage=1
# trainer_interface.cc(592) LOG(INFO) Done! preprocessed 91 sentences.
# unigram_model_trainer.cc(265) LOG(INFO) Making suffix array...
# unigram_model_trainer.cc(269) LOG(INFO) Extracting frequent sub strings... node_num=873
# unigram_model_trainer.cc(312) LOG(INFO) Initialized 301 seed sentencepieces
# trainer_interface.cc(598) LOG(INFO) Tokenizing input sentences with whitespace: 91
# trainer_interface.cc(609) LOG(INFO) Done! 189
# unigram_model_trainer.cc(602) LOG(INFO) Using 189 sentences for EM training
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=0 size=218 obj=13.3298 num_tokens=575 num_tokens/piece=2.63761
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=1 size=205 obj=12.5123 num_tokens=579 num_tokens/piece=2.82439
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=0 size=153 obj=12.9447 num_tokens=631 num_tokens/piece=4.12418
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=1 size=153 obj=12.7215 num_tokens=631 num_tokens/piece=4.12418
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=0 size=114 obj=14.0652 num_tokens=715 num_tokens/piece=6.27193
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=1 size=114 obj=13.7569 num_tokens=715 num_tokens/piece=6.27193
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=0 size=110 obj=13.8304 num_tokens=724 num_tokens/piece=6.58182
# unigram_model_trainer.cc(618) LOG(INFO) EM sub_iter=1 size=110 obj=13.7909 num_tokens=724 num_tokens/piece=6.58182
# trainer_interface.cc(687) LOG(INFO) Saving model: hindi_tokenizer.model
# trainer_interface.cc(699) LOG(INFO) Saving vocabs: hindi_tokenizer.vocab
# ['▁म', 'श', 'ी', 'न', '▁', 'ल', 'र्', 'न', 'ि', 'ं', 'ग', '▁मह', 'त्', 'व', 'पूर्', 'ण', '▁है', '।']