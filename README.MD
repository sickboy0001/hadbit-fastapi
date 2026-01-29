
- [hadbit-fastapi](#hadbit-fastapi)
  - [🚀 プロジェクト概要](#-プロジェクト概要)
  - [🛠 技術スタックと選定理由](#-技術スタックと選定理由)
  - [📋 基本仕様](#-基本仕様)
    - [1. 開発・実行環境](#1-開発実行環境)
    - [2. フロントエンド](#2-フロントエンド)
    - [3. バックエンド \& BaaS](#3-バックエンド--baas)
  - [📂 ディレクトリ構成](#-ディレクトリ構成)
  - [🚢 デプロイフロー](#-デプロイフロー)
  - [要件](#要件)
    - [非機能要件](#非機能要件)
    - [スタート画面](#スタート画面)
    - [登録画面](#登録画面)
    - [マスタ編集画面](#マスタ編集画面)
    - [統計画面](#統計画面)
  - [画面一覧とURL設計](#画面一覧とurl設計)
  - [各画面の責務](#各画面の責務)
    - [1. スタート画面 (`/dashboard`)](#1-スタート画面-dashboard)
    - [2. 登録画面 (`/records`)](#2-登録画面-records)
    - [3. マスタ編集画面 (`/HadbitSettings`)](#3-マスタ編集画面-hadbitsettings)
    - [4. 統計画面 (`/analytics`)](#4-統計画面-analytics)
  - [論理構成図（テーブル定義）](#論理構成図テーブル定義)
    - [1. Users (ユーザー情報)](#1-users-ユーザー情報)
    - [2. habit\_items (習慣項目マスタ)](#2-habit_items-習慣項目マスタ)
    - [3. habit\_item\_tree (習慣項目階層管理)](#3-habit_item_tree-習慣項目階層管理)
    - [4. habit\_logs (実施記録)](#4-habit_logs-実施記録)
    - [構成のポイント](#構成のポイント)
  - [DDL](#ddl)
- [クエリ頑張る系](#クエリ頑張る系)


# hadbit-fastapi

Python + FastAPI + htmx + Docker + Render + Supabase を組み合わせた、開発効率とモダンなユーザー体験を両立させるためのフルスタック・テンプレートです。


## 🚀 プロジェクト概要

PFXDRS Templateは、ReactやVueなどの重厚なSPAフレームワークを使わずに、HTMLベースで動的なUIを実現する\*\*「ハイパーメディア駆動」\*\*な開発スタイルを提案します。
クリーンなディレクトリ構成とコンテナ化により、迅速な開発からデプロイまでをスムーズに行える構成になっています。

---

## 🛠 技術スタックと選定理由

base:PFXDGRSbase

|技術要素|役割・選定理由|
|-|-|
|**Python / FastAPI**|サーバーサイドの主軸。Router/Service層を分けたクリーンな構成の学習と実践。|
|**htmx**|フロントエンドのUX向上。HTMLベースで動的な非同期通信を実現し、複雑さを軽減。|
|**DaisyUI (Tailwind CSS)**|UIコンポーネントライブラリ。直接CSSを書く手間を省き、一貫したデザインを迅速に構築。|
|**Docker**|環境のポータビリティ確保。Render以外のホスト環境への移行も容易にするため。|
|**Render**|サーバーサイドおよびDockerとの親和性が高く、Vercel以外の有力な選択肢として採用。|
|**Supabase**|データベース(PostgreSQL)および認証基盤(Auth)として利用。|

---

## 📋 基本仕様

### 1\. 開発・実行環境

* **エディタ**: Visual Studio Code (VS Code)
* **開発支援**: Gemini Code Assist
* **ランタイム**: Python 3.11+ / Docker
* **パッケージ管理**: pip (`requirements.txt`)

### 2\. フロントエンド

* **テンプレートエンジン**: Jinja2 (サーバーサイドレンダリング)
* **非同期通信**: htmx (Partial HTMLの差し替え)
* **スタイリング**: DaisyUI (Tailwind CSSベースのコンポーネント)

### 3\. バックエンド \& BaaS

* **Webフレームワーク**: FastAPI
* **バリデーション**: Pydantic
* **DB/Auth**: Supabase (PostgreSQL / Supabase Auth)
* **SDK**: `supabase-py`

---

## 📂 ディレクトリ構成

```
localProject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/
    ├── main.py
    ├── models/          # 【Model】DBテーブル定義 (SQLAlchemy等)
    ├── schemas/         #  入出力バリデーション (Pydantic)
    ├── services/        # 【Business Logic】ここに計算やDB処理を書く
    │   └── item_service.py
    ├── routers/         # 【Controller】ルーティングとViewの制御
    │   └── item_router.py
    ├── templates/       # 【View】HTML (Jinja2)
    │   ├── base.html
    │   └── items/
    │       └── list.html
    └── static/          # 静的ファイル
        ├── css/
        └── js/
```

---

## 🚢 デプロイフロー

Renderを利用したCI/CDが自動化されています。

1. **GitHubへPush**: `main` ブランチへコードをプッシュ。
2. **ビルド**: Renderがリポジトリの `Dockerfile` を検知し、Dockerイメージをビルド。
3. **自動デプロイ**: ビルド成功後、Web Serviceとして自動デプロイ。
4. **環境変数管理**: Render Dashboardおよびローカルの `.env` で秘匿情報を管理。

---

Dockerでの起動方法
ターミナルを開く VS Code で Ctrl + J（または Ctrl + @）を押してターミナルを開きます。

Dockerイメージのビルド 以下のコマンドを実行して、現在のディレクトリ（.）の Dockerfile からイメージを作成します。

```bash
docker build -t testloginrendar .
```

-t testloginrendar: イメージに名前（タグ）を付けます。
コンテナの起動 ビルドが成功したら、以下のコマンドで起動します。

```bash
docker run --rm -p 8000:10000 --env-file .env --name my-test-container testloginrendar
```

--rm: 停止時にコンテナを自動削除します（検証用に便利）。
-p 8000:10000: ホストのポート 8000 をコンテナの 10000 に転送します。
--env-file .env: .env ファイルがある場合、環境変数を読み込みます（docker-compose では自動ですが、docker run では指定が必要です）。 .env については xxxURL="xxxx" はNG　xxxURL=xxxx　はOK　ダブルコーテーションは省くこと。 
検証 ブラウザで http://localhost:8000 にアクセスして動作を確認します。 停止するにはターミナルで Ctrl + C を押します。


## 要件
### 非機能要件
- **表示順の変更:** よく使うボタンを上に持ってくる（ソート機能）は必要
  - マスタ編集画面で変更して、それに合わせて登録画面で作成する
- **完了状態の可視化:** 登録画面の下のほうに、登録済みのデータが見えるようにする。

###  スタート画面
- 最初にログインしたときに見える画面です。
- ここから「登録画面」や「マスタ編集画面」「統計画面」に遷移する
### 登録画面
- ログイン後利用可能
- 登録された習慣化マスタから画面を作成して、習慣化の記録を残す
- 例えば、マスタとして運動→階段利用があったときには、階段利用のボタンを準備
- 押下することで、階段利用を行ったこと登録する

- **記録の単位:** 「「1日に何度も」押せるのか（例：階段利用は1日何回も発生する）。
- **取り消し機能:** 間違えてボタンを押した場合、その場で削除・修正は可能。トーストで表示、編集、削除を展開できる
- **日付の概念:** デフォルトは今日だが、編集画面で日時は変更できることとする

###  マスタ編集画面
- 習慣化したい項目について登録する
- マスタ自体は階層化機能をもつ
- 基本はタイトル、項目の親子関係をもつ
  - 運動→ランニング、運動→スクワッド、運動→クランク、学習→Schoo、学習→Audible、余暇→のみ、余暇→外食など
- **階層の深さ:** 親→子の2階層固定
- **マスタの削除・変更:** 既に記録があるマスタ（例：「ランニング」）を削除したり名前を変えたりした場合、過去の記録は更新された状態で見える
 
### 統計画面
- 何をどの程度習慣化して実施した見れる画面
- 指定された項目、カテゴリーを、日ごと、週ごと、月ごとにどれだけ実施したか見れる画面にする
- カレンダー形式のヒートマップ、週間の棒グラフでの展開が可能



## 画面一覧とURL設計

| 画面名 | URL (Path) | 画面名（システム上の識別子） | 説明 |
| --- | --- | --- | --- |
| **スタート画面** | `/dashboard` | `DashboardView` | ログイン後の拠点となるポータル。各機能へのハブ。 |
| **登録画面** | `/hadbit/records` | `hadbit_recordrds` | 習慣化マスタをボタン表示し、実績を記録するメイン画面。 |
| **マスタ編集画面** | `/hadbit/Settings` | `hadbit_settings` | カテゴリや項目の階層構造、表示順を設定する画面。 |
| **統計画面** | `/hadbit/analytics` | `hadbit_analytics` | 日・週・月ごとの実施状況を可視化する画面。 |
| **（詳細・編集）** | `/hadbit/records/:id/edit` | `RecordEditView` | 登録した記録の日時修正や削除を行うための詳細画面。 |

## 各画面の責務

### 1. スタート画面 (`/dashboard`)

* **導線:** `/records`, `/HadbitSettings`, `/analytics` への大きなナビゲーションボタンを配置。
* **状態:** ログインしていない場合は `/login` へリダイレクトする制御が必要です。

### 2. 登録画面 (`/records`)

* **動的生成:** `/HadbitSettings` で定義された「表示順」に従ってボタンを配置します。
* **履歴表示:** 画面下部にその日の履歴一覧を表示。
* 各履歴の「編集」ボタンから `/records/:id/edit` へ遷移、またはモーダルで対応。

### 3. マスタ編集画面 (`/HadbitSettings`)

* **構造:** 親カテゴリ（運動など）の中に子項目（ランニングなど）をネストして表示。
* **ソート:** ドラッグ＆ドロップ、または「↑↓」ボタンで順序を入れ替え、その順序（`sort_order`）をDBに保存します。

### 4. 統計画面 (`/analytics`)

* **フィルタリング:** `category_id` や `item_id` で絞り込み。
* **期間切り替え:** クエリパラメータを使って `/analytics?period=weekly` のように状態を保持すると、ブラウザの戻るボタンが効くので便利です。

---

## 論理構成図（テーブル定義）

### 1. Users (ユーザー情報)

※テーブル定義のSQLには含まれていませんでしたが、各テーブルから参照されているため、一般的な構成で記載します。

| カラム名 | データ型 | NULL許容 | 説明 | 主キー/その他 |
| --- | --- | --- | --- | --- |
| id | SERIAL | NO | ユーザーの一意識別ID | 主キー |
| user_name | TEXT | NO | ログインユーザー名 |  |

---

### 2. habit_items (習慣項目マスタ)

習慣化したいアクション自体の情報を保持するメインマスタです。

| カラム名 | データ型 | NULL許容 | 説明 | 主キー/その他 |
| --- | --- | --- | --- | --- |
| **id** | SERIAL | NO | 項目の一意識別ID | 主キー |
| user_id | INTEGER | NO | 所有者ユーザーのID | 外部キー (Users.id) |
| name | TEXT | NO | 習慣の名前（例：「階段利用」） |  |
| short_name | TEXT | YES | 略称 |  |
| description | TEXT | YES | 項目の詳細説明 |  |
| parent_flag | BOOLEAN | YES | 親カテゴリかどうかのフラグ | デフォルト: false |
| public_flag | BOOLEAN | YES | 公開設定 | デフォルト: false |
| visible_flag | BOOLEAN | YES | 画面表示の有無 | デフォルト: true |
| delete_flag | BOOLEAN | YES | 論理削除フラグ | デフォルト: false |
| item_style | JSONB | YES | UI用スタイル設定（色、アイコン等） | JSON形式 |
| updated_at | TIMESTAMP | NO | 最終更新日時 | 既定値: CURRENT_TIMESTAMP |
| created_at | TIMESTAMP | NO | レコード作成日時 | 既定値: CURRENT_TIMESTAMP |

---

### 3. habit_item_tree (習慣項目階層管理)

項目の親子関係と、表示順序を管理する構造テーブルです。

| カラム名 | データ型 | NULL許容 | 説明 | 主キー/その他 |
| --- | --- | --- | --- | --- |
| **item_id** | INTEGER | NO | 対象の項目ID | 主キー / 外部キー (habit_items.id) |
| parent_id | INTEGER | YES | 親カテゴリの項目ID | 外部キー (habit_items.id) |
| order_no | INTEGER | YES | 画面上の表示順序 |  |

---

### 4. habit_logs (実施記録)

ユーザーが習慣を実行した際の履歴データです。

| カラム名 | データ型 | NULL許容 | 説明 | 主キー/その他 |
| --- | --- | --- | --- | --- |
| **id** | SERIAL | NO | 記録の一意識別ID | 主キー |
| user_id | INTEGER | NO | 実施したユーザーのID | 外部キー (Users.id) |
| item_id | INTEGER | NO | 実施した項目のID | 外部キー (habit_items.id) |
| done_at | TIMESTAMP | YES | 習慣を実施した日時 |  |
| comment | TEXT | YES | 実施時のメモ、一言 |  |
| updated_at | TIMESTAMP | NO | 記録の最終更新日時 | 既定値: CURRENT_TIMESTAMP |
| created_at | TIMESTAMP | NO | レコード作成日時 | 既定値: CURRENT_TIMESTAMP |

---

### 構成のポイント

* **階層構造の実現**: `habit_item_tree` で `parent_id` が `NULL` のものを取得すれば「親カテゴリ」、特定の `parent_id` を持つものを取得すれば「そのカテゴリに属する子項目」として抽出可能です。
* **表示順の制御**: `habit_item_tree` の `order_no` を書き換えることで、ユーザーごとに自由な並び替え（非機能要件）に対応しています。
* **カスケード削除**: `habit_item_tree` には `on delete CASCADE` が設定されているため、`habit_items` から物理削除された場合、自動的にツリー構造からも除外されるようになっています。

こ
## DDL

```sql

create table public.mail_to_id (
  id serial not null,
  mail text not null,
  constraint mail_to_id_pkey primary key (id)
) TABLESPACE pg_default;

create table public.habit_item_tree (
  item_id integer not null,
  parent_id integer null,
  order_no integer null,
  constraint habit_item_tree_pkey primary key (item_id),
  constraint fk_habit_item_tree_item_id foreign KEY (item_id) references habit_items (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_habit_item_tree_item_id on public.habit_item_tree using btree (item_id) TABLESPACE pg_default;

create table public.habit_items (
  id serial not null,
  user_id integer not null,
  name text not null,
  short_name text null,
  description text null,
  parent_flag boolean null default false,
  public_flag boolean null default false,
  visible_flag boolean null default true,
  delete_flag boolean null default false,
  updated_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  created_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  item_style jsonb null,
  constraint habit_items_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_habit_items_user_id on public.habit_items using btree (user_id) TABLESPACE pg_default;

create table public.habit_logs (
  id serial not null,
  user_id integer not null,
  item_id integer not null,
  done_at timestamp without time zone null,
  updated_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  created_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  comment text null,
  constraint habit_logs_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_habit_logs_user_id on public.habit_logs using btree (user_id) TABLESPACE pg_default;

create index IF not exists idx_habit_logs_item_id on public.habit_logs using btree (item_id) TABLESPACE pg_default;
```

# クエリ頑張る系
```sql
SELECT 
  hp.id as parent_id, 
  hp.name as parent_name, 
  hp.short_name as parent_short_name,
  hit.order_no as parent_order_no,
  hi.description as parent_description ,
  hi.id , hi.name , hi.short_name,
  hi.description
FROM habit_items hi
INNER JOIN habit_item_tree hit 
  ON hi.id = hit.item_id
INNER JOIN habit_items hp 
  ON  hit.parent_id = hp.id 
WHERE hi.user_id = 1
order by hit.order_no
```