

<!-- Page 1 -->

- Include a link to the original paper in your reference list.


# Attention Is All You Need  


Ashish Vaswani<sup>1</sup> Google Brain avaswani@google.com  


Noam Shazeer<sup>2</sup> Google Brain noash@gmail.com  


Niki Parmar<sup>3</sup> Google Research nikitp@google.com  


Jakob Uszkoreit<sup>4</sup> Google Research usz@goolge.com  


Lilou Jones<sup>5</sup> Google Research lilou@google.com  


Aidan N. Gomez<sup>1</sup> University of Toronto aidan@cs.toronto.edu  


Lukasz Kaiser<sup>6</sup> Google Brain lukaszalaskier@google.com  


## Illia Polosukhin<sup>7</sup>  


illia.polosukhinsgmail.com  


## Abstract  


The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolution layers altogether. Our model is trained end-to-end using only unlabeled text as supervision to acquire multi- billion word parallelizable and requiring significantly less time to train. Our model achieves \(28.8 \mathrm{BLEU}\) on the WMT 2014 Englishto-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single- model state-of-the-art BLEU score of 41.0 after training for 9.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.  


## Introduction  


Recurrent neural networks, long short- term memory [2] and gated recurrent [3] neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation [20][23]. Numerous efforts have since continued to push the boundaries of recurrent language models and encoder- decoder architectures [10][11][13].


<!-- Page 2 -->

- Avoid using images in your text; use a link instead.


Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states \( h_t \), as function of the previous hidden state \( h_{t-1} \) and the input position \( t \). This inherently sequential nature precludes parallelism within training examples, which becomes critical at longer sequences. To address this limitation, researchers have proposed various approaches such as recurrently significant improvements in computational efficiency through factorization tricks [13] and conditional computation [28], while also improving model performance in case of the latter. The fundamental constraint of sequential computations, however, remains: 


Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their duration in the input or output sequences [210]. In that it has a few cases [23], however, we admit attention machines are used in conjunction with a recurrent network. 


In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs. 


## 2 Background 


The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU [25]. ByteNet [25] and ConvS3X [8], all of which use convolutional neural networks as basic building block, computing hidden representations related for all input and output positions. In these models, the number of operations required to realize signals from two arbitrary input or output positions grows in the distance between positions. Invariably ConvS3X and logarithmically for ByteNet. This makes it more difficult to learn dependencies between the outputs [10]. In the Transformer this is achieved by introducing self-attention operations, albeit at the cost of reduced effective resolution due to averaging attentional weights' positions, an effect we constructed with Multi-Head Attention as described in section2.4. 


Self-attentions, sometimes called intra-attentions in an attentive mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attentions has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations [612][213][219]. 


End-to-end memory networks are based on a recurrent attention mechanism instead of sequence-aligned recurrence and have been shown to perform well on simple-language question answering and language modeling tasks [22]. 


To be the end of knowledge, however, the Transformer is the first transformation model relying entirely on self-attentional compute representations in input and output without using sequence aligned RNNs or activations. In the following sections, we will show the Transformer, motivate self-attention and discuss its advantages over models such as [133] [5] and [6]. 


### 3 Model Architecture 


Most competitive neural sequence transduction models have an encoder-decoder structure [619][29]. Here, the encoder maps an input sequence of symbol representations \((x_1,\ldots,x_n)\) to a sequence of continuous representations \(\mathbf{z} = \{z_1,\ldots,z_m\}\). Given \(\mathbf{x}\) , the decoder then generates an output sequence \((\hat{y}_1,\ldots,\hat{y}_m)\) of symbols one element at a time. At each step the model is auto-regressive [20], consuming the previously generated symbols as additional input when generating the next. 


The Transformer follows this overall architecture using stacked self-attention and point-wise fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure[7] respectively. 


### 3.1 Encoder and Decoder Stacks 


**Encoder:** The encoder is composed of a stack of \(N=6\) identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position


<!-- Page 3 -->

<center>Figure 1: The Transformer - model architecture.</center>  


wise fully connected feed- forward network. We employ a residual connection [10] around each of the two sub-layers, followed by layer normalization [1]. That is, the output of each sub-layer is LayerNorm(\(x + \mathrm{Sublayer}(x)\)), where \(\mathrm{SubLayer}(x)\) is the function implemented by the sub- layer itself. To facilitate these residual connections, all sub- layers in the model, as well as the embedding layers, produce outputs of dimension \(d_{\mathrm{model}} = 512\) .  


Decoder: The decoder is also composed of a stack of \(N = 6\) identical layers. In addition to the two sub- layers in each encoder layer, the decoder inserts a third sub- layer, which performs multi- head attention on top output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub- layers, followed by layer normalization. We also modify the self- attention sub- layer in the decoder stack to prevent positions from attending to subsequent positions. This masking, combined with last that its output embeddings are offset by one position, ensures that the predictions of position \(i\) can depend only on the known outputs at positions less than \(i\) .  


### 3.2 Attention  


An attention function can be described as mapping a query and a set of key- value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key.  


#### 3.2.1 Scaled Dot-Product Attention  


We call our particular attention "Scaled Dot- Product Attention" (Figure 2). The input consists of queries and keys of dimension \(d_{k}\) , and values of dimension \(d_{v}\) . We compute the dot products of the


<!-- Page 4 -->

<center>Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.</center>  


query with all keys, divide each by \(\sqrt{d_{k}}\) , and apply a softmax function to obtain the weights on the values.  


In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix \(Q\) . The keys and values are also packed either into matrices \(K\) and \(V\) . We compute the matrix of outputs as:  


\[\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\biggl (\frac{Q K^{\top}}{\sqrt{d}}\biggr)V \quad (1)\]  


The two most commonly used attention functions are additive attention \(\boxed{\mathbf{A}}\) , and dot-product (multiplicative) attention. Dot-product attention is identical to our algorithm, except for the scaling factor of \(\frac{1}{\sqrt{d_k}}\) . Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.  


While for small values of \(d_{k}\) the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of \(d_{k}\) . Q. We suspect that for large values of \(d_{k}\) , the dot products grow large in magnitude, pushing the softmax function into regions where it extremely small gradients. To counteract this effect, we scale the dot products by \(\frac{1}{\sqrt{d_{k}}}\) .  


#### 3.2.2 Multi-Head Attention  


Instead of performing a single attention function with \(d_{\mathrm{head}}\) - dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values \(q\) times with different, learned linear projections to \(d_{h}, d_{k}\) and \(d_{v}\) dimensions, respectively. On each of these projected versions of queries, keys and values, we then perform the attention function in parallel, yielding \(d_{k}\) - dimensional vectors from which we concatenated and once again projected, resulting in the final values, as depicted in Figure 3.  


Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this


<!-- Page 5 -->

Where the projections are parameter matrices \(W_{1}^{Q} \in \mathbb{R}^{(d_{\mathrm{out}})\times d_{\mathrm{L}}} , W_{1}^{K} \in \mathbb{R}^{(k_{\mathrm{out}}\times d_{\mathrm{L}})}, W_{1}^{V} \in \mathbb{R}^{(k_{\mathrm{out}}\times d_{\mathrm{V}})}\) and \(W^{O} \in \mathbb{R}^{(k_{\mathrm{o}}\times k_{\mathrm{out}})}.\)  


In this work we employ \(h = 8\) parallel attention layers, or heads. For each of these we use \(d_{\mathrm{L}} = d_{\mathrm{v}}, d_{\mathrm{output}} / h = 64\) . Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.  


#### 3.2.3 Applications of Attention in our Model  


The Transformer uses multi-head attention in three different ways:  


a. In "encoder-decoder attention" layers, the queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder. This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models such as BERT. b. The encoder contains self-attention layers. It's an self-attention layer all of the keys, values and queries come from the same place; in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder.   


Similarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. We need to prevent leftward propagation through the decoder if it attends to a position at time step \(t > t_0\) by using attention units inside of scaled dot-product attention by masking out (setting \(\mathbf{x} = - \mathbf{x}\) ) until values in the input of the decoder which correspond to illegal connections. See Figure 2.  


### 3.3 Position-wise Feed-Forward Networks  


In addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically. This consists of two linear transformations with an ReLU activation function:  

\[\operatorname {FFN}(x) = \max (0,x\mathbf{W}_1 + b_1)\mathbf{W}_2 + b_2\]  


While the linear transformations are the same across different positions, they use different parameters from layer to layer. Another way of describing this is as two convolutions with kernel size 1. The dimensionality of input and output is \(d_{\mathrm{input}} = 512\) , and the inner-layer has dimensionality \(d_{ff} = 2048\) .  


#### 3.4 Embeddings and Softmax  


Similarly to other sequence transformation modules, we use learned embeddings to convert the input token and output location to vectors of dimension \(d_{\mathrm{token}}\) . We also use the usual learned linear transformation and softmax function to convert the decoder output to predicted next-token probabilities. In our model, we share the same weight matrix between the two embedding layers and the pre-softmax linear transformation, similar to Eq. (2). In the embedding layers, we multiply those weights by \(\sqrt{d_{\mathrm{token}}}\) .  


## 3.5 Positional Encoding  


Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. To this end, we add "positional encodings" to the input embeddings at the


<!-- Page 6 -->

- Avoid using images in your report.

Table I: Maximum path lengths, per-layer complexity and minimum number of sequential operations for different layer types \(i\) is the sequence length, \(\beta\) is the representation dimension, \(k\) is the kernel size of convolution and \(r\) the stride of the convolutional kernel in the resized self-attention block.

| Layer Type | Complexity Per Layer | Sequential | Maximum Path Length |
|------------|----------------------|-----------|--------------------|
| Self-Attention | \(O(n^2 \cdot d)\) | \(O(1)\)     | \(O(1)\)              |
| Recurrent    | \(O(n \cdot d + c^2)\)   | \(O(n)\)     | \(O(n)\)             |
| Convolution  | \(O(k \cdot n + d^2)\)   | \(O(1)\)     | \(O(log_3(n))\)       |
| Self-Attention (restricted) | \(O(r \cdot n \cdot d)\) | \(O(1)\)     | \(O(n/r)\)          |

bottoms of the encoder and decoder stacks. The positional encodings have the same dimension \(d_{model}\) as the embeddings, so that the two can be summed. There are many choices of positional encodings, learned and fixed \((\mathbf{f})\)  

In this work, we use sine and cosine functions of different frequencies:

\[PE_{(pos,n)} = sin(pos/1000)^{2/(d_{model})} \\
EP_{(pos,n+1)} = cos(pos/1000)^{2/(d_{model})}\]

where pos is the position and n is the dimension. That is, each dimension of the positional encoding corresponds to a neural state. The non-linear transformation function from the x=10000, z=50, thus the chosen function because we hypothesized it would allow the model to easily learn to attend by relative positions, since far away (far off-center), \(E.P_{(pos,n)}\) can be represented as a linear function of \(PE_{(pos)}\). 

We also experimented with using learned positional embeddings \(\mathbf{ID}_{n}^{j}\) instead, and found that the two versions produced nearly identical results (see Table [Show Example]). We chose the sinusoidal version because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training.

4 Why Self-Attention

In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping raw variable-length sequences of symbol representations \((x_{1},...,x_{n})\) to another sequence of equal length \((z_{1},...,z_{n})\), which \(x_{i}\in Z^{l}\), where A is a hidden layer in a typical sequence transformer encoder or decoder. Motivating our use of self-attention was consider three desiderata.  
One is the total computational complexity per layer. Another is the amount of computation that can be parallelised, as measured by the minimum number of sequential operations required. This third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transformers tasks. Once Key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals how to traverse in the network. The shorter these paths between any combination of positions in the input and output sequence, the easier it is to learn long-range dependencies \((\mathbf{I})\). Hence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types. As noted at Section 3, attention mechanisms require an additional parameter space to represent the context vector.


<!-- Page 7 -->

- Avoid using images in your text; they can be difficult to read and may cause issues with accessibility.


the input sequence centered around the respective output position. This would increase the maximum path length to \(O(n / r)\). We plan to investigate this approach further in future work. 


A single convolutional layer with kernel width \(k < n\) does not connect all pairs of input and output positions. Doing so requires a stack of \((n / k)\) convolutional layers in the case of contiguous kernels, or \(O((\log_2 n))\) in the case of dilated convolutions [12], increasing the length of the longest paths between any two positions in the network. Convolutional layers are generally more expensive than recurrent layers, by a factor of \(\frac{n}{r}\). Example considerations [8] however, decrease the complexity considerably, to \(O(k \cdot d + w \cdot c/r)\). Even with \(w = n\), however, the complexity of a separable convolution is still exponential in the number of self-attention layers and a point-wise feed-forward layer, the approach we take in our model. 


As side benefit, self-attention could yield more interpretable models. We inspect attention distributions from our models and present and discuss examples in the appendix. We only do individual attention heads (early) learn to perform different tasks, many appear to exhibit behavior related to the syntactic and semantic structure of the sentences. 


## 5 Training 


This section describes the training regime for our models. 


### 5.1 Training Data and Batching 


We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using byte-pair encoding [3], which has a shared source-target vocabulary of about 37000 tokens. For English-French, we used the significant larger WMT 2014 English-French dataset consisting of 50M sentences and split tokens into a 32000 word piece vocabulary [31]. Sentence pairs were batched together by approximate sequence length. Each training batch contains a set of sentence pairs containing approximately 25000 source tokens and 25000 target tokens. 


### 5.2 Hardware and Scheduler 


We trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We trained the base models for a total of 100,000 steps or 12 hours. For our big models(described on the bottom line of table[5]), step time was 1.0 seconds. The big models were trained for 300,000 steps (3.5 days). 


### 5.3 Optimizer 


We used the Adam optimizer [17] with \(\beta_{1} = 0.9, \beta_{2} = 0.98\) and \(\epsilon = 10^{-6}\). We varied the learning rate over the course of training, according to the formula: 


\[rate = \pi_{\max}^{(\alpha)} \min(step_num^{0.75}, step_num \cdot warmup\_steps^{1 - b}) \quad (25)\]


This corresponds to increasing the learning rate linearly for the first \(warmup\_steps\) training steps, and decreasing it thereafter proportionally to the inverse square root of the step number. We used \(warmup\_step = 4800\). 


### 5.4 Regularization 


We employ three types of regularization during training: 


**Residual Dropout** We apply dropout [27] to the output of each sub-layer, before it is added to the sub-layer input and normalized. In addition, we apply dropout to the sums of the embeddings and the positional encodings in both the encoder and decoder stacks. For the base model, we use a rate of \(Targ = 0.1\).


<!-- Page 8 -->

Table 2: The Transformer achieves better BLEU scores than previous state-of-the-art models on the English-to-German and English-to-French newsstories2014 testset at a fraction of the training cost.

<table><tr><td rowspan="3">Model</td><td colspan="5">BLEU1</td></tr><tr><td>EN-DE</td><td>EN-BF</td><td>FR-DE</td><td>EN-FR</td><td></td></tr><tr><td>25.75</td><td>39.2</td><td></td><td></td><td></td></tr><tr><td>ByteSeq [15]</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Deep-Lm + PoLMix [28]</td><td>24.6</td><td>39.92</td><td>2.3×10¹⁰</td><td>1.4×10²⁵</td><td></td></tr><tr><td>GNNIT + RL [21]</td><td>25.16</td><td>46.46</td><td>9.0×10³</td><td>1.5×10⁴⁶</td><td></td></tr><tr><td>Cos-SSIS [26]</td><td>25.16</td><td>40.45</td><td>2.0×10¹⁷</td><td>1.2×10²⁸</td><td></td></tr><tr><td>MoE [20]</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Deep-Lm + PoLMix Ensemble [33]</td><td>26.30</td><td>41.14</td><td>1.5×10²⁹</td><td>1.1×10³⁰</td><td></td></tr><tr><td>GNNIT + RL Ensemble [31]</td><td>26.30</td><td>41.19</td><td>7.7×10²⁹</td><td>1.1×10³¹</td><td></td></tr><tr><td>CosSSI Ensemble [36]</td><td>26.35</td><td>42.18</td><td>7.3×10³¹</td><td>3.3×10⁴⁴</td><td></td></tr><tr><td>Transformer (base model)</td><td>27.3</td><td>38.1</td><td></td><td>3.3×10⁴⁵</td><td></td></tr><tr><td>Transformer (big)</td><td>**28.4**</td><td>41.0</td><td>2.3×10⁵⁹</td><td></td><td></td></tr></table>


Label Smoothing During training, we employed label smoothing of value \(s_{L} = 0.1\) [50]. This hurts perplexity, as the model learns to be more sure, but improves accuracy and BLEU score.


# 6 Results


## 6.1 Machine Translation


On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big)) in Table 3 outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4. The configuration of this model is identical to that used in Table 2 during Training task 3.5 days so FID@100 GRFs. Even one less model surpasses all previously published models and ensembles, at a fraction of the training cost of any of the compared models.


On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41.0, outperforming all of the previous published single model results, aloee its team 1/4 the training cost of the previous state-of-the-art model. The significant (big) result gained four English-to-French sub-datasets:


For the base models, we used a single model obtained by averaging the last 5 checkpoints, which were written in 10-minute intervals. For the big models, we averaged both an IOU checkpoint. We used beam search with a beam size of 4 and length penalty \(\alpha = 0.05\) . These hyperparameters were chosen after experimentation on the development set. We see the maximum output length during inference to input length $=50$ ,but terminate early when possible [32].


Table 3 summarizes our results and compares our translation quality and training costs to other model architectures from the literature. We estimate the number of floating point outputs needed to train a model by multiplying the training time, the number of GPUs used, and an estimate of the sustained single-precision-floating-point capacity of each GPU.1


## 6.2 Model Variations


To evaluate the importance of different components of the Transformer, we varied our base model in different ways, measuring the change in performance on English-to-German translation on the development set, newsstory2013. We used beam search as described in the previous section, but no checkpoint averaging. We present these results in Table 3.


In Table 3(one), A(x) we vary the number of attention heads and the attention layer's total dimension, keeping the amount of computation constant, as described in Section 3.2[52]. While single-head attention is 0.9 BLEU worse than the best setting, quality also drops off with too many heads.


<!-- Page 9 -->

<table><tr><td></td><td>\(N\)density</td><td>\(d_{H}\)</td><td>\(h\)</td><td>\(d_{b}\)</td><td>\(d_{c}\)</td><td>\(P_{\text {exp}}\) \(e_{L}\)</td><td>train<br>(dev)</td><td>PPLL</td><td>BLEU</td><td>params<br>&lt;10<sup>-6</sup></td></tr><tr><td rowspan="3">base</td><td>6</td><td>512</td><td>2048</td><td>8</td><td>64</td><td>0.1</td><td>0.1</td><td>100K</td><td>4.92</td><td>25.8</td><td>65</td></tr><tr><td>1</td><td>5</td><td>32</td><td>12</td><td></td><td></td><td></td><td>5.29</td><td>24.9</td><td></td><td></td></tr><tr><td>(A)</td><td></td><td></td><td>4</td><td>128</td><td>128</td><td></td><td></td><td>5.00</td><td>25.5</td><td></td></tr><tr><td></td><td></td><td></td><td>16</td><td>32</td><td>32</td><td></td><td></td><td>4.91</td><td>25.8</td><td></td><td></td></tr><tr><td>(B)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>5.01</td><td>25.4</td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>5.16</td><td>25.1</td><td></td><td>58</td></tr><tr><td>(C)</td><td>2</td><td></td><td></td><td></td><td></td><td></td><td></td><td>5.11</td><td>25.4</td><td>60</td><td></td></tr><tr><td></td><td>4</td><td></td><td></td><td></td><td></td><td></td><td></td><td>6.11</td><td>23.7</td><td>30</td><td></td></tr><tr><td></td><td>8</td><td>256</td><td></td><td>32</td><td></td><td></td><td></td><td>4.88</td><td>25.3</td><td>50</td><td></td></tr><tr><td></td><td>1024</td><td></td><td></td><td>128</td><td>128</td><td></td><td></td><td>5.75</td><td>24.8</td><td>28</td><td></td></tr><tr><td></td><td>4096</td><td></td><td></td><td></td><td></td><td></td><td></td><td>4.66</td><td>26.0</td><td>18</td><td></td></tr><tr><td>(D)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>4.77</td><td>25.2</td><td>20</td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td>0.0</td><td></td><td></td><td>5.77</td><td>24.6</td><td>90</td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>4.95</td><td>25.5</td><td></td><td></td></tr><tr><td>(E)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>4.67</td><td>25.1</td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>5.47</td><td>25.7</td><td></td><td></td></tr><tr><td>(Exp.)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>4.27</td><td>25.7</td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>In Table[Brows (B), we observe that reducing the attention key size \(d_{k}\) hurts model quality. This suggests that determining compatibility is not easy and that a more sophisticated compatibility function that can reduce trust may be beneficial. We further observe in rows (C) and (D) that, as expected, bigger models are better, and dropout is very helpful in avoiding over-fitting. In row (E) we replace our sinusoidal positional encoding with learned positional embeddings \(\mathbf {\Xi }_{i}^{l}\), and observe nearly identical results to the base model.</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>


# 7 Conclusion


In this work, we presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention.


For translation tasks,the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers. As in both WMT 2014 plug-ins-Genius and WMT 2014 English-to-French translation tasks,we achieve a new state of the art. In the former task one best model outperforms even all previously reported ensembles.


We are well aware that the future of automatic head models and plan to apply them to other tasks: We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local,restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video. Making generation less sequential is another research goals of ours.


The code we used to train and evaluate our models is available at https://github.com/ [tensorflow/tensorflow]


<!-- Page 10 -->

- Avoid using images as links; use descriptive file names instead.

## References


[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016. 


[2] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. CoRR, abs/1409.0473, 2014. 


[3] Denny Britz, Anna Gulcehre, Minh-Thang Luong, and Quoc V Le. Massive exploration of neural machine translation architectures. CoRR, abs/1703.03906, 2017. 


[4] Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine reading. arXiv preprint arXiv:1610.06715, 2016. 


[5] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. CoRR, abs/1406.1078, 2014. 


[6] Francois Chollet. Xception: Deep learning with depthwise separable convolutions. arXiv preprint arXiv:1610.02368, 2016. 


[7] Junyoung Chung, Caglar Gulcehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. CoRR, abs/1412.3555, 2014. 


[8] Jonas Gehrig, Michael Auli, David Grangier, Denis Yarats, and Yann Dauphin. Convolutional sequence to sequence learning. arXiv preprint arXiv:1705.03122v2, 2017. 


[9] Alex Graves. Generating sequences with recurrent neural networks. arXiv preprint arXiv:1308.0850, 2013. 


[10] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pages 770–778, 2016. 


[11] Sepp Hochreiter, Yoshua Bengio. Pulse Networks and Jitgum Schmidtmeier: Gradient flow in recurrent time: the difficulty of learning long-term dependencies, 2001. 


[12] Sepp Hochreiter and Jurgen Schmidhuber. Long short-term memory. Neural computation, 08(13):1735–1780, 1997. 


[13] Rafał Jozefowicz, Oriol Wipfyan, Mike Schuster, Noam Shazeer, and Yonghui Wu. Exploring the limits of language modelling. arXiv preprint arXiv:1602.02410, 2016. 


[14] Lukasz Kaiser and Ilya Sutskever. Neural GPUs learn algorithms. In International Conference on Learning Representations (ICLR), 2016. 


[15] Nal Kalchbrenner, Lasse Espeholt, Karen Simonyan, Aaron van den Oord, Alex Graves, and Koray Kavukcuoglu. Neural machine translation in linear time. arXiv preprint arXiv:1610.10099v2, 2017. 


[16] Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks. In International Conference on Learning Representations, 2017. 


[17] Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In ICLR, 2015. 


[18] Oleksii Kuchaiev and Boris Ginsburg. Factorization tricks for LSTM networks. arXiv preprint arXiv:1703.10272, 2017. 


[19] Zhouhan Liu, Minwei Feng, Cicero Neugarte dos Santos, Mo Yu, Bing Xiang, Bowen Zhou, and Yoshua Bengio. A structured self-attentive sentence embedding. arXiv preprint arXiv:1703.05130, 2017. 


[20] Samy Bengio Lukasz Kaiser. Can active memory replace attention? In Advances in Neural Information Processing Systems, (NIPS), 2016.


<!-- Page 11 -->

- Ensure that all images are properly referenced with their respective file paths and alt text.


[21] Minh-Thang Luong, Hieu Pham, and Christopher D Manning. Effective approaches to attention-based neural machine translation. arXiv preprint arXiv:1508.04025, 2015. 


[22] Ankur Parikh, Oscar Täckström, Dipanjan Das, and Jakob Uszkoreit. A decomposable attention model. In Empirical Methods in Natural Language Processing, 2016. 


[23] Romain Paulus, Caiming Xiong, and Richard Socher. A deep reinforced model for abstractive summarization. arXiv preprint arXiv:1703.04304, 2017. 


[24] Ofir Press and Lev Wolf. Using the output embedding to improve language models. arXiv preprint arXiv:1608.05859, 2016. 


[25] Rico Sennrich, Barry Haddow, and Alexandra Birch. Neural machine translation of rare words with subword units. arXiv preprint arXiv:1508.07909, 2015. 


[26] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton, and Jeff Dean. Outrageously large neural networks: The sparsely-gated mixture-of-experts layer. arXiv preprint arXiv:1701.06538, 2017. 


[27] Nitish Srivastava, Geoffrey E Hinton, Alex Krizhevsky, Ilya Sutskever, and Ruslan Salakhutdinov. Dropout: a simple way to prevent neural networks from overfitting. Journal of Machine Learning Research, 15(1):1929–1958, 2014. 


[28] Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, and Rob Fergus. End-to-end memory networks. In E. Cortes, N. D. Lawrence, D. D. Lee, M. Sugiyama, and R. Garnett, editors, Advances in Neural Information Processing Systems 28, pages 2440–2448. Curran Associates, Inc., 2015. 


[29] Ilya Sutskever, Oriol Vinyals, and Quoc VV Le. Sequence to sequence learning with neural networks. In Advances in Neural Information Processing Systems, pages 3104–3112, 2014. 


[30] Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jonathon Shlens, and Zbigniew Wojna. Rethinking the inception architecture for computer vision. CoRR, abs/1512.00567, 2015. 


[31] Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V Le, Mohammad Norouzi, Wolfgang Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, et al. Google's neural machine translation system: Bridging the gap between human and machine translation. arXiv preprint arXiv:1609.08144, 2016. 


[32] Jie Zhou, Ying Cao, Xuguang Wang, Peng Li, and Wei Xu. Deep recurrent models with fast-forward connections for neural machine translation. CoRR, abs/1606.04199, 2016.
