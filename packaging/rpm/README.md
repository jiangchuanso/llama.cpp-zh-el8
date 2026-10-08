# llama-cpu RPM

面向 EL8 及其兼容系统（CentOS / Rocky / AlmaLinux 8、麒麟高级服务器 V10）的
预编译 CPU 版 [llama.cpp](https://github.com/jiangchuanso/llama.cpp-zh-el8) 推理服务。

本包把二进制**以及**它们配套的 C++ 运行库（`libstdc++.so.6`、`libgomp.so.1`）一起
放在 `/opt/llama-cpu` 下，通过 `$ORIGIN` rpath 加载，因此不依赖宿主机的 `libstdc++`
版本。这正是对接麒麟 V10 的关键——麒麟的 `libstdc++` 只到 `GLIBCXX_3.4.24`，而本包
自带的是 `3.4.25`，靠 $ORIGIN 自包含解决了版本不兼容。

## 目录结构

| 路径 | 内容 |
| ---- | ------- |
| `/opt/llama-cpu/bin/` | `llama-server`、`llama-cli`、`llama-bench`、`libllama*.so`、`libggml*.so`，以及随包带的 `libstdc++.so.6` / `libgomp.so.1` |
| `/usr/bin/llama-*` | 指向 `/opt/llama-cpu/bin` 的软链接 |
| `/etc/llama-cpu/models.ini` | 路由模式的模型 preset（`--models-preset` 指向的文件，必须存在） |
| `/usr/lib/systemd/system/llama-server.service` | systemd 单元文件；启动参数内联在其 `ExecStart`（用 `systemctl edit llama-server` 覆盖） |
| `/var/lib/llama-cpu/` | 服务家目录，可写（模型放在 `models/` 下） |

## 安装

按架构选包：

| 架构 | 要装的包 |
| --- | --- |
| x86_64（Intel / AMD / 海光） | `llama-cpu-<版本>.<release>.el8.x86_64.rpm` |
| aarch64（飞腾） | `llama-cpu-<版本>.<release>.el8.aarch64.rpm` |

x86_64 只有一个包：AVX2 / AVX512 / AMX 等指令集变体由运行时按 CPUID 自动选择，无需按厂商区分。

```sh
# 安装
sudo rpm -ivh llama-cpu-0.4.1-1.b11053.el8.x86_64.rpm
# 或者升级到新版本
sudo rpm -Uvh llama-cpu-0.4.1-1.b11054.el8.x86_64.rpm
```

本包**不写任何全局库路径**：运行库只放在 `/opt/llama-cpu/bin` 下，由同目录的二进制通过
`$ORIGIN` rpath 加载，不写 `/usr/lib64`、不改 `/etc/ld.so.conf`、不需要 `LD_LIBRARY_PATH`。

spec 里用 `AutoReqProv: no` 关闭了自动依赖扫描，因此包内既**不依赖**、也**不宣告**
`libstdc++.so.6` / `libgomp.so.1`，只声明 `glibc >= 2.28` 与 `systemd`。如果用 `dnf`
安装时报缺失运行库的错，那是打包 bug，请用 `rpm -qp --requires <file.rpm>` 把依赖列表
反馈上来。

## CUDA 附加包（llama-cuda，可选）

`llama-cuda` 给本包加 NVIDIA GPU 加速，自身**不含**可执行文件、服务或配置，只往
`/opt/llama-cpu/bin` 放一个文件：

| 路径 | 内容 |
| ---- | ---- |
| `libggml-cuda.so*` | CUDA 后端，llama-server 启动时在自己目录里发现并加载它 |

CUDA 运行库**不随包提供**（cudart + cublas 有数百 MB），由目标机自行安装，见下面的说明。

只发布 x86_64 一种架构：

```sh
sudo rpm -Uvh llama-cpu-<版本>.<release>.el8.x86_64.rpm \
              llama-cuda-<版本>.<release>.el8.x86_64.rpm
```

- `llama-cuda` 用 `Requires: llama-cpu = <完全相同的 Version-Release>` 精确锁定，两个包必须
  来自同一次发布。升级时也要**一条命令同时升级两个包**，只升 `llama-cpu` 会因依赖不满足而失败
  （两个包都升则正常）。
- 目标机需要自己提供两样东西，缺任一样后端都不会被加载（服务照旧纯 CPU 运行）。两者都用
  NVIDIA 官方的 Linux runfile 安装器装，不随包、也不走 RPM：
  1. **CUDA 13.x 运行库**：至少 `libcudart.so.13` 与 `libcublas.so.13`（`libcublas` 自己会带出
     `libcublasLt`）。用与构建同版本的 runfile（如 `cuda_13.0.0_580.95.05_linux.run`，仅装
     runtime/toolkit 时加 `--toolkit`）安装，装完把 `/usr/local/cuda-13.0/lib64` 写进
     `/etc/ld.so.conf.d/` 后 `ldconfig`，或者把 `libcudart.so.13`、`libcublas.so.13`、
     `libcublasLt.so.13` 直接放到 `/opt/llama-cpu/bin/`（后端带 `$ORIGIN` rpath，同目录优先）。
  2. **NVIDIA 驱动**：提供 `libcuda.so.1`。本包按 CUDA 13 构建，对应 580 系列驱动
     （>= 580.26，具体看所用 CUDA 13 小版本捆绑的驱动版本）；驱动同样用官方 `.run` 安装器装。
- 装好后不用改配置：`--n-gpu-layers` 默认为 `auto`，按显存自动决定往 GPU 放几层。想强制不用
  GPU 就传 `--n-gpu-layers 0`，或直接 `rpm -e llama-cuda`。
- 后端按上游默认的 CUDA 架构集合编译（Maxwell 及更新的卡都能用）。
- nightly 里除了 RPM 还有对应的 tarball `llama-cuda-el8-x64-<版本>.tar.gz`，解压到
  `llama-cpu-el8-x64-<版本>.tar.gz` 解压出来的同一个目录即可，效果与装 RPM 相同。

## 配置

```sh
sudo cp ~/model.gguf /var/lib/llama-cpu/models/
sudo chown llama-cpu:llama-cpu /var/lib/llama-cpu/models/model.gguf
sudo systemctl edit llama-server   # 覆盖 ExecStart 里的启动参数
```

服务默认以**路由模式**启动（`--models-dir` + `--models-preset`）：`models/` 目录下的每个
`.gguf` 自动注册为一个模型，模型 id 就是文件名去掉 `.gguf` 后缀。请求通过 `"model"`
字段选择模型，首次请求时按需加载，驻留数超过 `--models-max`（默认 4）时按 LRU 自动卸载。

启动参数已内联在 `llama-server.service` 的 `ExecStart` 里：

```sh
ExecStart=/opt/llama-cpu/bin/llama-server \
    --host 0.0.0.0 --port 8080 \
    --models-dir /var/lib/llama-cpu/models \
    --models-preset /etc/llama-cpu/models.ini
```

要改参数，最干净的方式是 `sudo systemctl edit llama-server` 生成 drop-in 覆盖
`ExecStart`；也可以直接改 `/usr/lib/systemd/system/llama-server.service`。

`--models-preset` 指向的文件**必须存在**，否则服务启动即失败；包内已自带
`/etc/llama-cpu/models.ini`（`%config(noreplace)`，升级不会覆盖你的修改）。需要给某个
模型单独设置 ctx / 线程 / 预加载（`load-on-startup`）时，在 ini 里加一个以模型 id 命名的
小节即可。模型目录为空也能启动，只是 `/v1/models` 列表为空。

### 线程数

`models.ini` 的 `[*]` 段随包设置了两个线程参数，数值**按架构在打包时写入**：

| 架构 | `threads`（生成） | `threads-batch`（prompt 处理） |
| ---- | ---- | ---- |
| x86_64（Intel Xeon / 海光） | 16 | 32 |
| aarch64（飞腾） | 8 | 32 |

这两项不设时，llama-server 会使用**全部逻辑核**，在核多的机器上反而极慢：飞腾
S5000C（128 核）的生成速度会从 8 线程的 32.5 t/s 掉到 128 线程的 2.3 t/s。

上表数值是用 1B Q8_0 模型在 Xeon E5-2620 v4、Hygon C86-3G 5380、Phytium S5000C
上实测得到的。x86_64 一档要同时兼容前两者，而它们的生成侧最优分别是 32 和 4 线程，
16 是折中；prompt 处理两侧都偏好 32。换用明显更大的模型后建议按 `llama-bench`
重新测一遍：

```sh
/opt/llama-cpu/bin/llama-bench -m /var/lib/llama-cpu/models/<model>.gguf \
  -p 512 -n 128 -t 4,8,16,32,64 -r 3 -o md
```

路由模式下**每个模型是独立的子进程**，各自持有自己的线程池，所以 `--models-max`
（默认 4）个模型同时推理时线程总数会成倍增长。若确定会有多个模型并发，可把
`threads-batch` 调低。

注意 `models.ini` 是 `%config(noreplace)`：`rpm -Uvh` 升级**不会**覆盖你改过的文件。
从旧版本升级后，若想用新的线程默认值，需要手动同步这一段，或删掉该文件后
`rpm reinstal`。

要退回**单模型模式**，把 `-m /var/lib/llama-cpu/models/model.gguf` 加回
`llama-server.service` 的 `ExecStart` 即可。

完整参数请用 `/opt/llama-cpu/bin/llama-server --help` 查看。模板已覆盖：模型、CPU/线程、
上下文与 KV 缓存类型、采样默认值、API 密钥、CORS、TLS、监控指标、embeddings/reranking、
日志。

**默认即启用**的选项刻意未列出（连续批处理、`--jinja`、`--warmup`、`--slots`、
`--cache-prompt`、多模态自动加载、Web UI 等）。若确需关闭其中某项，传对应的 `--no-<opt>`。

每个 flag 也都有对应的 `LLAMA_ARG_*` 环境变量形式，例如 `-c/--ctx-size` 等价于
`LLAMA_ARG_CTX_SIZE`。

## 运行

```sh
sudo systemctl enable --now llama-server
systemctl status llama-server
journalctl -u llama-server -f
```

本 RPM **故意不**随包启用服务：先往 `/var/lib/llama-cpu/models/` 放入至少一个模型
（空目录也能启动，但没有任何模型可用）。服务失败会自动重启，但 60 秒内重试 5 次仍失败
就放弃，避免错误配置造成无限重启风暴。

## 验证

```sh
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/v1/models   # 路由模式：列出 models/ 下发现的模型
# 设置了 API key 时：
curl -s -H "Authorization: Bearer <key>" http://127.0.0.1:8080/v1/models
```

一次对话补全（路由模式下 `"model"` 必填，填文件名去掉 `.gguf` 后缀的 id）：

```sh
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3-8B-Q8_0","messages":[{"role":"user","content":"hello"}],"max_tokens":32}'
```

Web UI 地址为 `http://<host>:8080/`（已内置中文界面）。不用的话加 `--no-webui` 关闭。

## 安全

除非设置 `--api-key`，否则 API **没有任何鉴权**。绑定 `0.0.0.0` 会把服务暴露给整个网络——
在共享或不可信网络中请务必设置 API key，或者只绑定 `127.0.0.1` 再用反向代理前置。

单元文件已启用 `NoNewPrivileges`、`PrivateTmp`、`ProtectSystem=full` 与
`ProtectHome=read-only`。若模型放在 `/var/lib/llama-cpu` 之外，记得在单元文件里把该目录
加入 `ReadOnlyPaths=`。

## 升级 / 卸载

```sh
sudo rpm -Uvh llama-cpu-<new>.rpm   # /etc/llama-cpu/models.ini 等配置保留（noreplace）
sudo rpm -e llama-cpu               # 保留 /var/lib/llama-cpu 及其模型
```
