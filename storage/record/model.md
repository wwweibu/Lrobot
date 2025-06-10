- [讯飞模型调用方法](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_1-%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E)
- 有时莫名调用不了工具
- 20w token
```
{
    "role": "assistant",
    "tool_calls": {
        "type": "function",
        "function": {"arguments": '{"txt":"abc"}', "name": "get_symbol"},
    },
}
```
- [混元模型调用方法](https://cloud.tencent.com/document/product/1729/111007)
- 100w token
```
{
    "content": "用户想要使用尼古拉加密法加密一个字符串'abc'。我需要调用get_symbol工具来加密字符串'abc'。\n\t\n\t调用get_symbol工具来加密字符串'abc'。",
    "refusal": None,
    "role": "assistant",
    "annotations": None,
    "audio": None,
    "function_call": None,
    "tool_calls": [
        {
            "id": "call_d070ap42c3m19dophv10",
            "function": {"arguments": '{"txt":"abc"}', "name": "get_symbol"},
            "type": "function",
            "index": 0,
        }
    ],
}
```
- [火山方舟引擎调用方法](https://www.volcengine.com/docs/82379/1399008)
- 50w token
```
{
    "content": "\n",
    "refusal": None,
    "role": "assistant",
    "annotations": None,
    "audio": None,
    "function_call": None,
    "tool_calls": [
        {
            "id": "call_h8fha7mo7xdc44s65y4fit2o",
            "function": {"arguments": '{"txt": "abc"}', "name": "get_symbol"},
            "type": "function",
        }
    ],
}
```
- [硅基流动调用方法](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions#llm)
- 5000 TPM
```
{
    "role": "assistant",
    "content": "",
    "tool_calls": [
        {
            "id": "019677d5f9312482e36d2016f6b5a67e",
            "type": "function",
            "function": {"name": "get_symbol", "arguments": '{"txt": "abc"}'},
        }
    ],
}
```
- [智谱清言调用方法](https://www.bigmodel.cn/dev/api/normal-model/glm-4)
- 免费
```
{
    "content": None,
    "role": "assistant",
    "tool_calls": [
        {
            "id": "call_-8760983896639489558",
            "function": {"arguments": '{"txt": "abc"}', "name": "get_symbol"},
            "type": "function",
            "index": 0,
        }
    ],
}
```
- ollama 本地调用
```
{
    "role": "assistant",
    "content": "",
    "images": None,
    "tool_calls": [{"function": {"name": "get_symbol", "arguments": {"txt": "abc"}}}],
}
```