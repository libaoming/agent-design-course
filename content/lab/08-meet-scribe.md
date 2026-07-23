---
title: meet-scribe
nav: meet-scribe
section: lab
status: open-source
repo: https://github.com/libaoming/meet-scribe
slug: meet-scribe
tags: [会议纪要, 本地转写, 无人值守]
summary: 线下会议自动纪要：录音 → 本地转写 + 说话人分离 → claude 生成纪要 → 落 Obsidian，全程无人值守。
order: 8
---

> 线上会议早就有自动纪要了，线下会议还停留在「散会以后凭记忆补」。把录音丢给云端 ASR 又有两个别扭：会议内容出了本机，转写按分钟计费。meet-scribe 把整条链路搬回本地：录音结束文件一落盘，launchd 自动接手——WhisperX 本地转写、pyannote 说话人分离、`claude -p` 生成纪要、写进 Obsidian vault——音频不出本机，零边际成本，没有守护进程也没有数据库。

## 它解决什么

| 痛点 | 方案 |
|---|---|
| 线下会议纪要靠手写 | 录音自动变成带说话人的结构化纪要 |
| 云端 ASR 的隐私与成本 | 模型全本地跑，音频不出本机，零边际成本 |
| 不想维护常驻服务 | 无 daemon 无数据库，launchd WatchPaths 文件触发 |

## 核心机制：目录即状态机

两个入口：Mac 上 `meet start/stop` 起停录音；iPhone 用语音备忘录录完，经 iCloud 的 MeetInbox 目录自动流入。之后一切由文件驱动——

音频落盘 → launchd WatchPaths 触发 → `bin/pipeline.sh` 单接缝四步：ffmpeg 转 16kHz wav → whisperx 中文转写 + 说话人分离 → 填 prompt 调 `claude -p` 出纪要 → 写 Obsidian 并归档。目录本身就是状态机：inbox / processing / archive / error，一眼看清每条录音走到哪一步。人只做三件事：起停命名、校正说话人姓名、执行纪要里的 TODO。

## 怎么用

`bin/meet start 会议名` 开录、`bin/meet stop` 收工，或者把任意音频丢进 `~/Meetings/inbox/` 即自动处理。换机部署：uv venv + ModelScope 拉模型（转写模型 1.5GB + 中文对齐模型 1.2GB，国内直连可达）+ `M1/init.sh` 自检 + 装载 launchd plist。

## 一句话

把「开完会写纪要」这件事从你的待办清单上永久划掉——而且一分钱不花。
