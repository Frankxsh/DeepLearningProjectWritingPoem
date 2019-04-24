# coding: UTF-8

from config import *

class MODEL:
    """model class"""
    def __init__(self, trainData):
        self.trainData = trainData
        self.has_not_model = True

    def buildModel(self, wordNum, gtX, hidden_units=128, layers=2):#建立的神经网络的模型
        """build rnn"""
        with tf.variable_scope("embedding"): #embedding tf.nn.embedding_lookup 字转换为 向量
            embedding = tf.get_variable("embedding", [wordNum, hidden_units], dtype = tf.float32)
            inputbatch = tf.nn.embedding_lookup(embedding, gtX)
            # 嵌入可以通过很多网络类型进行训练，并具有各种损失函数和数据集。
            # 例如，对于大型句子语料库，可以使用递归神经网络根据上一个字词预测下一个字词，还可以训练两个网络来进行多语言翻译

        basicCell = tf.contrib.rnn.BasicLSTMCell(hidden_units, state_is_tuple = True)
        stackCell = tf.contrib.rnn.MultiRNNCell([basicCell] * layers)
        initState = stackCell.zero_state(np.shape(gtX)[0], tf.float32)
        outputs, finalState = tf.nn.dynamic_rnn(stackCell, inputbatch, initial_state = initState)
        outputs = tf.reshape(outputs, [-1, hidden_units])

        with tf.variable_scope("softmax"):
            w = tf.get_variable("w", [hidden_units, wordNum])
            b = tf.get_variable("b", [wordNum])
            logits = tf.matmul(outputs, w) + b

        probs = tf.nn.softmax(logits)
        return logits, probs, stackCell, initState, finalState

    def train(self, reload=True):
        """train model"""
        print("training...")
        gtX = tf.placeholder(tf.int32, shape=[batchSize, None])  # input
        gtY = tf.placeholder(tf.int32, shape=[batchSize, None])  # output

        logits, probs, a, b, c = self.buildModel(self.trainData.wordNum, gtX)
        # 查看一下gtY的内容及为什么变换格式
        targets = tf.reshape(gtY, [-1])

        #loss
        loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example([logits], [targets],
                                                                  [tf.ones_like(targets, dtype=tf.float32)])
        globalStep = tf.Variable(0, trainable=False)
        addGlobalStep = globalStep.assign_add(1)

        cost = tf.reduce_mean(loss)#计算平均损失
        trainableVariables = tf.trainable_variables()
        grads, a = tf.clip_by_global_norm(tf.gradients(cost, trainableVariables), 5) # prevent loss divergence caused by gradient explosion
        learningRate = tf.train.exponential_decay(learningRateBase, global_step=globalStep,
                                                  decay_steps=learningRateDecayStep, decay_rate=learningRateDecayRate)
        optimizer = tf.train.AdamOptimizer(learningRate)
        trainOP = optimizer.apply_gradients(zip(grads, trainableVariables))


        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()

            if not os.path.exists(checkpointsPath):
                os.mkdir(checkpointsPath)

            if reload:
                checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
                # if have checkPoint, restore checkPoint
                if checkPoint and checkPoint.model_checkpoint_path:
                    saver.restore(sess, checkPoint.model_checkpoint_path)
                    print("restored %s" % checkPoint.model_checkpoint_path)
                else:
                    print("no checkpoint found!")

            for epoch in range(epochNum):
                X, Y = self.trainData.generateBatch()
                epochSteps = len(X) # equal to batch
                for step, (x, y) in enumerate(zip(X, Y)):
                    a, loss, gStep = sess.run([trainOP, cost, addGlobalStep], feed_dict = {gtX:x, gtY:y})
                    print("epoch: %d, steps: %d/%d, loss: %3f" % (epoch + 1, step + 1, epochSteps, loss))
                    if gStep % saveStep == saveStep - 1: # prevent save at the beginning
                        print("save model")
                        saver.save(sess, os.path.join(checkpointsPath, type), global_step=gStep)

    def probsToWord(self, weights, words):
        """probs to word"""
        prefixSum = np.cumsum(weights) #prefix sum
        ratio = np.random.rand(1)
        index = np.searchsorted(prefixSum, ratio * prefixSum[-1]) # large margin has high possibility to be sampled
        return words[index[0]]

    def test(self):
        """write regular poem"""
        print("genrating...")
        gtX = tf.placeholder(tf.int32, shape=[1, None])  # input
        logits, probs, stackCell, initState, finalState = self.buildModel(self.trainData.wordNum, gtX)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()
            checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
            # if have checkPoint, restore checkPoint
            if checkPoint and checkPoint.model_checkpoint_path:
                saver.restore(sess, checkPoint.model_checkpoint_path)
                print("restored %s" % checkPoint.model_checkpoint_path)
            else:
                print("no checkpoint found!")
                exit(1)

            poems = []
            for i in range(generateNum):
                state = sess.run(stackCell.zero_state(1, tf.float32))
                x = np.array([[self.trainData.wordToID['[']]]) # init start sign
                probs1, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                word = self.probsToWord(probs1, self.trainData.words)
                poem = ''
                sentenceNum = 0
                while word not in [' ', ']']:
                    poem += word
                    if word in ['。', '？', '！', '，']:
                        sentenceNum += 1
                        if sentenceNum % 2 == 0:
                            poem += '\n'
                    x = np.array([[self.trainData.wordToID[word]]])
                    #print(word)
                    probs2, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                    word = self.probsToWord(probs2, self.trainData.words)
                print(poem)
                poems.append(poem)
            return poems

    def model_generlize(self):
        if self.has_not_model:
            gtX = tf.placeholder(tf.int32, shape=[1, None])  # input
            logits, probs, stackCell, initState, finalState = self.buildModel(self.trainData.wordNum, gtX)
            self.gtX = gtX
            self.logits = logits
            self.probs = probs
            self.stackCell = stackCell
            self.initState = initState
            self.finalState = finalState
            self.has_not_model = False

        return self.gtX, self.logits, self.probs, self.stackCell, self.initState, self.finalState


    def testHead(self, characters):
        """write head poem"""
        print("genrating...")
        gtX, logits, probs, stackCell, initState, finalState = self.model_generlize()
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()
            checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
            # if have checkPoint, restore checkPoint
            if checkPoint and checkPoint.model_checkpoint_path:
                saver.restore(sess, checkPoint.model_checkpoint_path)
                print("restored %s" % checkPoint.model_checkpoint_path)
            else:
                print("no checkpoint found!")
                exit(1)
            flag = 1
            endSign = {-1: "，", 1: "。"}
            poem = ''
            state = sess.run(stackCell.zero_state(1, tf.float32))
            x = np.array([[self.trainData.wordToID['[']]])
            probs1, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
            for word in characters:
                if self.trainData.wordToID.get(word) == None:
                    print("这个字好难呀，小姬不认识")
                    exit(0)
                flag = -flag
                while word not in [']', '，', '。', ' ', '？', '！']:
                    poem += word
                    x = np.array([[self.trainData.wordToID[word]]])
                    probs2, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                    word = self.probsToWord(probs2, self.trainData.words)

                poem += endSign[flag]
                # keep the context, state must be updated
                if endSign[flag] == '。':
                    probs2, state = sess.run([probs, finalState],
                                             feed_dict={gtX: np.array([[self.trainData.wordToID["。"]]]), initState: state})
                    poem += '\n'
                else:
                    probs2, state = sess.run([probs, finalState],
                                             feed_dict={gtX: np.array([[self.trainData.wordToID["，"]]]), initState: state})

            print(characters)
            print(poem)
            return poem