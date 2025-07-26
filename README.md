# 3×3写真マトリクス生成システム

MakeShop Print-on-Demand対応の写真マトリクス自動生成システム

## 🎯 概要

アップロードされた写真を自動的に最適配置し、美しい3×3マトリクスレイアウトの画像データを生成するシステムです。

### ✨ 特徴

- **写真配置最適化**: フォーカルポイント（右上）への印象的な写真配置
- **ハイブリッドレイアウト**: 写真比率に応じた最適レイアウト自動選択
- **MakeShop仕様準拠**: 2520×2520px、PNG形式、200dpi
- **透過背景対応**: 余白部分が透明なPNG出力
- **バッチ処理**: 大量写真の自動分割処理

## 🚀 クイックスタート

### 1. Manusでの使用方法

1. [3x3_photo_matrix_makeshop_specification.md](./3x3_photo_matrix_makeshop_specification.md) の内容をコピー
2. Manusにペーストして実行
3. 写真をアップロードして処理開始

### 2. ローカル環境での使用方法

```bash
# 必要なライブラリをインストール
pip install Pillow numpy scikit-learn

# 写真を配置
mkdir upload
# upload/ フォルダに写真を配置

# 実行
python matrix_generator.py upload output
```

## 📊 対応写真枚数

| 写真枚数 | 生成マトリクス数 | 説明 |
|---------|----------------|------|
| 1-8枚 | 1個 | 不足分は背景で補完 |
| 9枚 | 1個 | 完全な3×3マトリクス |
| 10-17枚 | 2個 | 9枚 + 残り枚数 |
| 18枚 | 2個 | 9枚 × 2 |
| 157枚 | 19個 | 9枚 × 17 + 8枚 |

## 🎨 レイアウトパターン

### スクエアレイアウト（正方形写真用）
- セルサイズ: 840×840px
- 写真比率: 0.9-1.1

### ランドスケープレイアウト（横長写真用）
- セルサイズ: 840×560px
- 写真比率: 1.1以上

### ポートレートレイアウト（縦長写真用）
- セルサイズ: 680×1020px
- 写真比率: 0.9未満

## 📁 ファイル構成

```
3x3-photo-matrix-generator/
├── README.md                                    # このファイル
├── 3x3_photo_matrix_makeshop_specification.md  # 完全仕様書
├── matrix_generator.py                          # 実装コード
└── examples/                                    # サンプル画像
    ├── sample_input/                           # 入力サンプル
    └── sample_output/                          # 出力サンプル
```

## 🔧 技術仕様

- **出力形式**: PNG（RGBA、透過対応）
- **解像度**: 2520×2520px（200dpi）
- **対応形式**: JPG、PNG、WEBP
- **最小サイズ**: 500×500px以上
- **配置原理**: 3×3グリッド + フォーカルポイント最適化

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

Issues、Pull Requestsを歓迎します！

## 📞 サポート

- バグ報告: [Issues](../../issues)
- 機能要望: [Issues](../../issues)
- 質問: [Discussions](../../discussions)

## 🔗 関連リンク

- **MakeShop Print-on-Demand**: https://www.makeshop.jp/main/function/print-on-demand/
- **Printio（印刷パートナー）**: MakeShopの印刷サービスを提供

## 📋 クレジット

このシステムは以下のサービス仕様に準拠して開発されました：
- **MakeShop**: ECサイト構築・Print-on-Demandサービス
- **Printio**: 高品質印刷サービスプロバイダー

---

**Powered by Manus AI** 🤖

