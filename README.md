# 机まるごと電子書籍化デバイス
## 説明
電気通信大学のアイデア実証コンテスト[U☆PoC2024](https://www.uec.ac.jp/research/venture/contest.html)に応募したアイデアの実装

## 使い方
筐体を組み立ててください．

## 環境
Python 3.8~3.11 (3.8と3.11で動作確認)

ultralytics 8.2.11~ (不明，最新版で動かなかったら8.2.11まで落としてください)(追記:最新版のほうがいいかも)

PyTorch 2.3.0  (torch) (ryusuke-m環境では2.5.1 -> 2.3.0へ落としたら動作しましたが，最新版でも一応動作するっぽい．不明)

バスエラー(コアダンプ)などが出たらPyTorchかultralyticsを疑ってください

PyRealsense2 (pyrealsense2) (Python 3.12に対応していない)

OpenCV4 4.9及び4.10で確認 (opencv-pythonとopencv-contrib-python)両方

## 実行
上記環境を整えてrealsenseをPCに接続(もしくはWebカメラを接続)
```
python3 Start.py
```

## e-desk
Practice of OpenCV and Machine Learning

2024/11/5ぐらい


