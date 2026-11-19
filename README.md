<div align="center">

# WeMM-Embedding-2B-GGUF

**Tencent WeMM-Embedding-2B 的 GGUF 量化版本与本地 `llama.cpp` 推理指南**

<p>
  <a href="https://www.modelscope.cn/models/huangyusi/WeMM-Embedding-2B-GGUF">
    <img src="https://img.shields.io/badge/ModelScope-下载模型权重-624AFF?style=flat-square" alt="ModelScope Download">
  </a>
  <a href="https://github.com/Tencent/WeMM-Embedding">
    <img src="https://img.shields.io/badge/Upstream-Tencent%2FWeMM--Embedding-0052D9?style=flat-square" alt="Upstream Repo">
  </a>
  <a href="https://arxiv.org/abs/2608.24053">
    <img src="https://img.shields.io/badge/arXiv-2608.24053-B31B1B?style=flat-square" alt="arXiv Paper">
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-2EA44F?style=flat-square" alt="License">
  </a>
  <img src="https://img.shields.io/badge/Format-GGUF-4B5563?style=flat-square" alt="GGUF">
  <img src="https://img.shields.io/badge/Runtime-llama.cpp-111827?style=flat-square" alt="llama.cpp">
</p>

</div>

> **声明 / Notice**
> 本仓库为社区维护的 **WeMM-Embedding-2B** GGUF 量化转换与使用指南仓库（非官方发布）。
> 原始模型由 **腾讯微信视觉团队（[@Tencent](https://github.com/Tencent) / [Tencent/WeMM-Embedding](https://github.com/Tencent/WeMM-Embedding)）** 研发并开源。
> 由于 GitHub 单文件体积限制，**所有 `.gguf` 模型权重均托管在魔搭社区（ModelScope）**，请前往魔搭社区下载。

---

## 简介

**WeMM-Embedding-2B-GGUF** 是腾讯 [WeMM-Embedding-2B](https://github.com/Tencent/WeMM-Embedding) 多模态嵌入模型的 GGUF 量化版本，面向本地 `llama.cpp` 推理部署，大幅降低显存与内存占用：

- **多模态统一表征**：支持文本、图像、视频、视觉文档及交错多模态输入（当前不支持音频输入）。
- **Matryoshka 可变维度**：默认输出 2,048 维 L2 归一化向量，支持灵活截断（如 64 / 128 / 256 / 512 / 1024 / 2048 维）。
- **多种量化精度**：提供 `Q4_K_M`、`Q6_K`、`Q8_0` 和 `BF16` 版本，并附带 `BF16` 精度 `mmproj` 视觉投影权重用于图像/视频嵌入。

---

## 模型下载（ModelScope 魔搭社区）

👉 **魔搭社区模型主页**：[https://www.modelscope.cn/models/huangyusi/WeMM-Embedding-2B-GGUF](https://www.modelscope.cn/models/huangyusi/WeMM-Embedding-2B-GGUF)

### 可用权重文件

| 文件名 | 大小 | 推荐用途 |
| --- | ---: | --- |
| `WeMM-Embedding-2B-Q4_K_M.gguf` | 1.56 GB | 默认推荐，体积与精度均衡 |
| `WeMM-Embedding-2B-Q6_K.gguf` | 1.97 GB | 更高保真度 |
| `WeMM-Embedding-2B-Q8_0.gguf` | 2.55 GB | 精度优先的量化版本 |
| `WeMM-Embedding-2B-BF16.gguf` | 4.79 GB | 原始参考精度 |
| `mmproj-WeMM-Embedding-2B-BF16.gguf` | 671 MB | **图像 / 视频输入必需**的视觉投影文件 |

> **提示**：主模型可按需选择量化版本；进行图像或视频多模态推理时，请搭配 `mmproj-WeMM-Embedding-2B-BF16.gguf` 使用。

### 方式一：使用 ModelScope CLI 下载（推荐）

```bash
# 1. 安装 ModelScope 客户端
python3 -m pip install -U modelscope

# 2. 仅下载推荐的文本嵌入模型（Q4_K_M）
modelscope download \
  --model huangyusi/WeMM-Embedding-2B-GGUF \
  --include 'WeMM-Embedding-2B-Q4_K_M.gguf' \
  --local_dir ./models
```

如需同时支持图像/视频多模态推理，可直接运行本仓库提供的一键下载脚本（同时下载 `Q4_K_M` 主模型与 `mmproj`）：

```bash
./scripts/download_modelscope.sh
```

### 方式二：网页直接下载

访问 [huangyusi/WeMM-Embedding-2B-GGUF 模型文件页](https://www.modelscope.cn/models/huangyusi/WeMM-Embedding-2B-GGUF/files)，按需点击下载对应 `.gguf` 文件即可。

### 完整性校验（SHA-256）

下载完成后，可使用本仓库的 [`SHA256SUMS`](./SHA256SUMS) 校验文件完整性：

```bash
# Linux
sha256sum -c SHA256SUMS

# macOS
shasum -a 256 -c SHA256SUMS
```

---

## 快速开始（`llama.cpp`）

请先安装较新版本的 [llama.cpp](https://github.com/ggml-org/llama.cpp)（Qwen3.5 架构与多模态 Embedding 依赖较新的运行时版本）。

### 1. 文本 Embedding

启动服务：

```bash
llama-server \
  -m ./models/WeMM-Embedding-2B-Q4_K_M.gguf \
  --embedding \
  --port 8080
```

调用 OpenAI 兼容接口：

```bash
curl http://127.0.0.1:8080/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"WeMM-Embedding-2B-Q4_K_M.gguf","input":"多模态检索测试"}'
```

> **注意**：模型元数据已指定 `qwen35.pooling_type=3`（对应 `llama.cpp` 的 `last` pooling，用于提取 `<embedding>` token），请**不要**使用 `--pooling mean` 覆盖。

### 2. 图像与视频 Embedding

同时加载主模型与 `mmproj` 视觉投影文件：

```bash
llama-server \
  -m ./models/WeMM-Embedding-2B-Q4_K_M.gguf \
  --mmproj ./models/mmproj-WeMM-Embedding-2B-BF16.gguf \
  --embedding \
  --port 8080
```

使用本仓库附带的客户端脚本发送请求：

```bash
# 图像 Embedding
python3 examples/llama_cpp_multimodal_embedding.py \
  --image ./image.jpg \
  --output image-embedding.json

# 视频 Embedding（支持通过 --dimension 指定 Matryoshka 截断维度）
python3 examples/llama_cpp_multimodal_embedding.py \
  --video ./video.mp4 \
  --dimension 256
```

> **重要 API 说明**：
> - 视频输入需要编译时启用了 FFmpeg/FFprobe 支持的 `llama.cpp`；客户端也支持 `--openai-compatible` 参数以调用 `/v1/embeddings`。
> - 请勿使用旧版 `image_data` + `[img-N]` 请求格式，当前 `llama.cpp` 可能将其当作纯文本静默忽略图像。请使用从 `/props` 获取的 `media_marker` 以及包含 `prompt_string` 与 `multimodal_data` 的请求体（[`examples/llama_cpp_multimodal_embedding.py`](./examples/llama_cpp_multimodal_embedding.py) 已自动处理）。

---

## 仓库目录结构

```text
.
├── README.md                                 # 项目说明与使用指南
├── LICENSE                                   # 开源协议（继承自上游 Apache-2.0）
├── SHA256SUMS                                # GGUF 模型权重 SHA-256 校验值
├── scripts/
│   └── download_modelscope.sh                # 魔搭社区一键下载脚本
└── examples/
    ├── llama_cpp_text.sh                     # 文本 Embedding 启动示例
    ├── llama_cpp_multimodal.sh               # 多模态 Embedding 启动示例
    └── llama_cpp_multimodal_embedding.py     # 图像 / 视频 Embedding Python 客户端
```

---

## 验证说明

本 GGUF 转换版本已完成以下基础校验：
- GGUF 文件可正常加载读取；
- 输出为 2,048 维归一化向量；
- `llama.cpp` 图像多模态推理路径可正常执行。

> 注意：原始模型的评测基准（Benchmark）成绩对应上游原始权重，不代表量化后 GGUF 模型的实测分数。

---

## 致谢与上游资源（Acknowledgements）

衷心感谢 **腾讯微信视觉团队（WeChat Vision Team, [@Tencent](https://github.com/Tencent)）** 开源了优秀的 **WeMM-Embedding** 系列模型，以及 [@ggml-org](https://github.com/ggml-org) 社区对 `llama.cpp` 和 GGUF 生态的贡献！

- **官方 GitHub 仓库**：[Tencent/WeMM-Embedding](https://github.com/Tencent/WeMM-Embedding)
- **官方魔搭社区模型**：[Tencent-Hunyuan/WeMM-Embedding-2B](https://www.modelscope.cn/models/Tencent-Hunyuan/WeMM-Embedding-2B)
- **官方 Hugging Face 合集**：[tencent/WeMM-Embedding](https://huggingface.co/collections/tencent/WeMM-Embedding)
- **技术报告（arXiv）**：[WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report](https://arxiv.org/abs/2608.24053)

---

## 引用（Citation）

如果您在研究或项目中使用了 WeMM-Embedding 模型，请引用原团队的技术报告：

```bibtex
@article{wemm-embedding,
  title={WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report},
  author={Junjie Zhou and Ke Mei and Lei Li and Tianyi Wang and Fengyun Rao and Jing Lyu},
  year={2026},
  eprint={2608.24053},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2608.24053}
}
```

---

## 开源协议（License）

本 GGUF 转换仓库**不改变**上游模型的原始开源协议，继续遵循 **Apache-2.0** 协议。在二次分发或商业使用前，请仔细阅读本仓库的 [`LICENSE`](./LICENSE) 文件以及 [上游模型卡片](https://www.modelscope.cn/models/Tencent-Hunyuan/WeMM-Embedding-2B) 中的相关条款。
