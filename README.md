# All-in-One Movie Generator

AI × YAMLで小説・脚本・映像・画像生成を一気通貫で自動化するワークフローシステム

## 特徴

- **YAML駆動**：全設定・プロンプト・テンプレートをYAMLで一元管理
- **AI自動最適化**：Gen-2/Pika/Fast SVD LCM/CogVideoX-5B等に対応
- **ペルソナ並列生成**：10ペルソナによる多様な草案生成と自動スコアリング
- **再帰的推敲**：最大15回の自動書き直し・フィードバック
- **知識ベース連携**：AIプロンプトTipsを自動取得・最適化

## ディレクトリ構成

```
allinonemovie/
├── main.yaml                 # メイン設定・エントリーポイント
├── creative_flow/            # ワークフロー・エンジン・依存パッケージ
│   ├── main_workflow.yaml    # ワークフロー定義
│   ├── workflow_engine.py    # 実行エンジン
│   ├── requirements.txt      # 必要パッケージ
│   └── user_prompt_questions.yaml # ユーザー入力テンプレ
├── includes/                 # テンプレ・知識ベース・エージェント定義
│   ├── ai_prompt_tips/       # AIプロンプトTipsキャッシュ
│   ├── agents_definition.yaml # エージェント・ペルソナ定義
│   ├── complete_ai_content_collection.yaml # AIプロンプト・モデル知識集
│   ├── workflow_checklist.yaml # 各工程のチェックリスト
│   ├── video_prompt_template.yaml # 映像AI用プロンプトテンプレ
│   ├── screenplay_template.yaml # 脚本テンプレ
│   ├── novel_template.yaml   # 小説テンプレ
│   ├── story_content_techniques.yaml # ストーリー技法集
│   ├── image_generation_techniques.yaml # 画像生成技法集
│   ├── t2v_doc.yaml         # Text-to-Video設定
│   ├── i2v_doc.yaml         # Image-to-Video設定
│   └── ...（その他テンプレ・技法・チェックリスト等）
├── .gitignore
└── README.md
```

## ワークフロー

1. **初期ヒアリング**：目的・主人公・舞台設定などを対話形式で取得
2. **草案プロトタイプ生成**：AIが複数案を自動生成
3. **レビュー＆分岐**：レビュー結果で次工程を自動選択
4. **映像化/他工程/既存プロセス**：分岐に応じて各種フローへ
5. **推敲ループ**：自動評価と最大15回の書き直し
6. **知識ベース参照**：AIモデルごとに最新Tipsを自動取得

## 主要ファイル

- `main.yaml`：全体設定・エントリーポイント
- `creative_flow/main_workflow.yaml`：ワークフロー定義
- `creative_flow/workflow_engine.py`：実行エンジン
- `includes/agents_definition.yaml`：エージェント・ペルソナ定義
- `includes/complete_ai_content_collection.yaml`：AIプロンプト・モデル知識集
- `includes/workflow_checklist.yaml`：各工程のチェックリスト
- `includes/video_prompt_template.yaml`：映像AI用プロンプトテンプレ
- `includes/screenplay_template.yaml`：脚本テンプレ
- `includes/novel_template.yaml`：小説テンプレ
- `includes/story_content_techniques.yaml`：ストーリー技法集
- `includes/image_generation_techniques.yaml`：画像生成技法集
- `includes/t2v_doc.yaml`：Text-to-Video設定
- `includes/i2v_doc.yaml`：Image-to-Video設定

## 依存パッケージ

- openai>=1.0.0
- python-dotenv>=1.0.0
- PyYAML>=6.0
- requests>=2.31.0
- beautifulsoup4>=4.12.0

## 使い方

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/nyattoh/allinonemovie.git
   cd allinonemovie
   ```

2. **仮想環境の作成・依存パッケージのインストール**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r creative_flow/requirements.txt
   ```

3. **main.yamlやincludes/内テンプレを編集**

4. **パイプライン実行**
   ```bash
   python creative_flow/workflow_engine.py
   ```

## 注意事項・推奨運用

- すべての設定・テンプレはYAMLで管理
- 各フェーズで最低15回の推敲を推奨
- Detarame要素（意外性）は整合性チェック必須
- AIモデルごとのプロンプト最適化は自動
- .venv/やキャッシュは.gitignoreで管理

## ライセンス

MIT License

## 貢献・連絡先

- Issue/Pull Request歓迎
- 質問・提案はGitHub Issueまで 