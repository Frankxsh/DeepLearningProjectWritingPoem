# 小小写诗姬

### 运用的技术和框架
- TensorFlow1.5-gpu：运用谷歌开源的Tensotflow机器学习框架进行写诗机器人的编写，运用Nvidia-cuda9.0 toolkit对模型深度学习进行加速训练
- 运用神经网络，循环神经网络RNN（recurrent neural network）中的LSTM模型（解决传统RNN模型的梯度消失和梯度爆发的问题）
- web前端运用bootstrap和materialize框架进行开发，使用live2D技术对canvas进行优化
- 运用python中的flask框架进行服务器端的编写，在保证功能的基础上，避免使用Django框架进行重型开发，达到在保证功能的基础上更快的反馈用户，给少的给机器运行的压力
- 考虑到第一次加载模型时间较长，避免用户第一次等待无聊，开发出“看板娘”canvas制作，并开启了“话痨多话”模式，每5秒自动向用户展示一句话（来源于互联网），解决用户和写诗模型的交互问题
- 在web前端中，使用jQuery和Ajax进行数据传输，减少更新内容带给服务器的压力，实现局部更新，更好更快的反馈用户所需要的模型写诗结果

### 技术原理简述：
- RNN LSTM模型原理
	- 传统的RNN模型，在训练的过程中的梯度下降过程中，更加倾向于按照序列结尾处的权值的正确方向进行更新。也就是说，越远的序列输入的对权值的正确变化所能起到的“影响”越小，所以训练的结果就是往往出现偏向于新的信息，即不太能有较长的记忆功能。
	- 长短期记忆模型（LSTM）是RNN模型的一种特殊结构类型，其增加了输入门、输出门、忘记门三个控制单元（“cell”），随着信息的进入该模型，LSTM中的cell会对该信息进行判断，符合规则的信息会被留下，不符合的信息会被遗忘。
##### 数据清洗过程：
- 数据来源：
	- 来自：https://github.com/chinese-poetry/chinese-poetry
	- 将json文件转变成模型可训练的文件排版
	- 进行数据清洗
- 数据清洗：
	- 清洗掉格式不对的，清洗掉有特殊符号的，清洗掉特殊字的，清洗掉格式异常的
	
- 模型搭建
	- 模型采用的是有两层隐藏层的神经网络，单元数是128，共享权重数据
	- 训练10个epoch，共需要43小时时间（使用gpu为 Nvidia-k660，3mirrors， 1G显存）
----

【数据及模型+完整项目】
百度云地址：https://pan.baidu.com/s/1vhxCkKhV5jxcZcHAlXZl9Q
分享码：ou00

答辩视频 https://www.bilibili.com/video/av50350607
