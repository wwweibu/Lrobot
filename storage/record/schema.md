filesystem中的可选参数是一个文件树
减少幻觉
[文本向量化](https://mp.weixin.qq.com/s?__biz=MzI5MzAxODU0NQ==&mid=2247484712&idx=2&sn=601089e6060988810519cf8d4ee3e9b2&chksm=ec79cbf6db0e42e0b1fb733efcafaaf9235a199c71d5ce6f8fccc4457f200365e0127d067d2f&scene=178&cur_album_id=3673740705999978504&poc_token=HMQH5GejkyCj0tV74OPVzZS9HihwUR1_ipQIXCsE)



各平台对于函数调用的支持：
openai和claude：支持MCP协议
各平台api：较新的支持MCP协议，免费的api里面只有glm-4-flash
ollama：部分标明tools的支持

各平台协议：
openai和claude：MCP协议，基于json schema，服务器模式/输入输出流模式，拓展了密钥，类型除了函数之外支持知识库、提示词
各平台api：传入json schema格式的数据
ollama：传入json schema格式的数据，除此之外，支持传入函数，以google tostring格式书写可自动解析

测试：
enum：qwen无法读取，glm能读取但还是会传入列表外的参数
format: 两个模型都能获取并且遵守
type：两个模型都能获取并传入符合参数类型的参数
descript：两个模型都能获取并且遵守
max/minLength：qwen无法读取，glm能读取但还是不会按照要求传入
