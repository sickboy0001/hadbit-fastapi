
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
    - [1. Users (auth.users / Supabase既存)](#1-users-authusers--supabase既存)
    - [2. hadbit\_items (習慣項目マスタ)](#2-hadbit_items-習慣項目マスタ)
    - [3. hadbit\_trees (習慣項目階層管理)](#3-hadbit_trees-習慣項目階層管理)
    - [4. hadbit\_logs (実施記録)](#4-hadbit_logs-実施記録)
    - [構成のポイント](#構成のポイント)
  - [DDL](#ddl)
- [クエリ頑張る系](#クエリ頑張る系)
    - [コンバートクエリ](#コンバートクエリ)
- [履歴](#履歴)


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

- [デプロイ先-Render-hadbit](https://hadbit-fastapi.onrender.com/dashboard)
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
検証 ブラウザで http://localhost:8000/docs にアクセスして動作を確認します。 停止するにはターミナルで Ctrl + C を押します。

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
| **マスタ編集画面** | `/hadbit/Items` | `hadbit_Items` | カテゴリや項目の階層構造、表示順を設定する画面。 |
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

### 1. Users (auth.users / Supabase既存)

Supabase Authが管理するユーザーテーブルです。

| カラム名 | データ型 | NULL許容 | 説明 | 備考 |
| --- | --- | --- | --- | --- |
| **id** | UUID | NO | ユーザーの一意識別ID | 主キー |
| email | TEXT | NO | メールアドレス |  |

---

### 2. hadbit_items (習慣項目マスタ)

習慣項目の基本情報を保持します。`user_id` が `UUID` に変更されています。

| カラム名 | データ型 | NULL許容 | 説明 | 備考 |
| --- | --- | --- | --- | --- |
| **id** | SERIAL | NO | 項目の一意識別ID | 主キー |
| **user_id** | **UUID** | NO | 所有者ユーザーのID | 外部キー (`auth.users.id`) |
| name | TEXT | NO | 習慣の名前 |  |
| short_name | TEXT | YES | 略称 |  |
| description | TEXT | YES | 詳細説明 |  |
| parent_flag | BOOLEAN | YES | 親カテゴリフラグ | デフォルト: false |
| public_flag | BOOLEAN | YES | 公開設定 | デフォルト: false |
| visible_flag | BOOLEAN | YES | 表示有無 | デフォルト: true |
| delete_flag | BOOLEAN | YES | 削除フラグ | デフォルト: false |
| **is_deleted** | BOOLEAN | YES | 削除状態（新設） | デフォルト: false |
| item_style | JSONB | YES | UIスタイル設定 | JSON形式 |
| updated_at | TIMESTAMP | NO | 最終更新日時 | 既定値: CURRENT_TIMESTAMP |
| created_at | TIMESTAMP | NO | レコード作成日時 | 既定値: CURRENT_TIMESTAMP |

---

### 3. hadbit_trees (習慣項目階層管理)

ツリー構造と並び順を管理します。今回の設計変更で **`user_id` が追加** されています。

| カラム名 | データ型 | NULL許容 | 説明 | 備考 |
| --- | --- | --- | --- | --- |
| **item_id** | INTEGER | NO | 対象の項目ID | 主キー / 外部キー (`hadbit_items.id`) |
| **user_id** | **UUID** | NO | 所有者ユーザーのID | 外部キー (`auth.users.id`) |
| parent_id | INTEGER | YES | 親項目のID | 0 または NULL でルート |
| order_no | INTEGER | YES | 表示順序 |  |

---

### 4. hadbit_logs (実施記録)

ユーザーの習慣実施履歴です。`user_id` が `UUID` に更新されています。

| カラム名 | データ型 | NULL許容 | 説明 | 備考 |
| --- | --- | --- | --- | --- |
| **id** | SERIAL | NO | 記録の一意識別ID | 主キー |
| **user_id** | **UUID** | NO | 実施したユーザーのID | 外部キー (`auth.users.id`) |
| item_id | INTEGER | NO | 対象の項目ID | 外部キー (`hadbit_items.id`) |
| done_at | TIMESTAMP | YES | 実施日時 |  |
| comment | TEXT | YES | 実施時のメモ |  |
| updated_at | TIMESTAMP | NO | 最終更新日時 | 既定値: CURRENT_TIMESTAMP |
| created_at | TIMESTAMP | NO | レコード作成日時 | 既定値: CURRENT_TIMESTAMP |


---

### 構成のポイント

* **階層構造の実現**: `habit_item_tree` で `parent_id` が `NULL` のものを取得すれば「親カテゴリ」、特定の `parent_id` を持つものを取得すれば「そのカテゴリに属する子項目」として抽出可能です。
* **表示順の制御**: `habit_item_tree` の `order_no` を書き換えることで、ユーザーごとに自由な並び替え（非機能要件）に対応しています。
* **カスケード削除**: `habit_item_tree` には `on delete CASCADE` が設定されているため、`habit_items` から物理削除された場合、自動的にツリー構造からも除外されるようになっています。

こ
## DDL
新テーブル対応
```sql

create table public.hadbit_items (
  id serial not null,
  user_id uuid not null,
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
  constraint hadbit_items_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_hadbit_items_user_id on public.hadbit_items using btree (user_id) TABLESPACE pg_default;


create table public.hadbit_trees (
  item_id integer not null,
  user_id uuid not null,
  parent_id integer null,
  order_no integer null,
  constraint hadbit_trees_pkey primary key (item_id),
  constraint fk_hadbit_trees_item_id foreign KEY (item_id) references hadbit_items (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_hadbit_trees_item_id on public.hadbit_trees using btree (item_id) TABLESPACE pg_default;

create table public.hadbit_logs (
  id serial not null,
  user_id uuid not null,
  item_id integer not null,
  done_at timestamp without time zone null,
  updated_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  created_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  comment text null,
  constraint hadbit_logs_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_hadbit_logs_user_id on public.hadbit_logs using btree (user_id) TABLESPACE pg_default;

create index IF not exists idx_hadbit_logs_item_id on public.hadbit_logs using btree (item_id) TABLESPACE pg_default;


```

# クエリ頑張る系
```sql
SELECT 
  -- 親アイテムの情報
  parent_item.user_id,
  parent_item.id           AS parent_id,
  parent_tree.order_no     AS parent_sort_order,
  parent_item.name         AS parent_name, 
  parent_item.short_name   AS parent_short_name,
  parent_item.description  AS parent_description,

  -- 子アイテムの情報
  child_tree.item_id       AS child_id,
  child_tree.order_no      AS child_sort_order,
  child_item.name          AS child_name,
  child_item.short_name    AS child_short_name,
  child_item.description   AS child_description 
FROM hadbit_trees AS parent_tree
INNER JOIN hadbit_items AS parent_item
  ON parent_tree.item_id = parent_item.id
  AND parent_item.user_id = 1
INNER JOIN habdit_trees AS child_tree
  ON child_tree.parent_id = parent_tree.item_id
INNER JOIN hadbit_items AS child_item
  ON child_tree.item_id = child_item.id
  AND child_item.user_id = 1
WHERE parent_tree.parent_id = 0
ORDER BY 
  parent_sort_order, 
  child_sort_order;

```
### コンバートクエリ
```sql 
DO $$
DECLARE
    -- ★ ここに対象ユーザーのメールアドレスを指定してください ★
    target_email text := 'syunjyu0001@gmail.com';
    
    old_user_id int;
    new_user_uuid uuid;
BEGIN
    -- 1. ユーザーIDの紐付け取得
    SELECT m.id, u.id INTO old_user_id, new_user_uuid
    FROM public.mail_to_id m
    JOIN auth.users u ON m.mail = u.email
    WHERE m.mail = target_email;

    IF old_user_id IS NULL OR new_user_uuid IS NULL THEN
        RAISE EXCEPTION 'ユーザーが見つかりません: %', target_email;
    END IF;

    -- 2. 新テーブルから対象ユーザーの既存データを削除 (外部キー CASCADE により tree も削除される)
    DELETE FROM public.hadbit_logs WHERE user_id = new_user_uuid;
    DELETE FROM public.hadbit_items WHERE user_id = new_user_uuid;

    -- 3. hadbit_items への移行
    -- id は指定せず PostgreSQL のシリアル採番に任せる
    INSERT INTO public.hadbit_items (
        user_id, name, short_name, description, 
        parent_flag, public_flag, visible_flag, delete_flag, 
        updated_at, created_at, item_style, is_deleted
    )
    SELECT 
        new_user_uuid, name, short_name, description, 
        parent_flag, public_flag, visible_flag, delete_flag, 
        updated_at, created_at, item_style, delete_flag
    FROM public.habit_items
    WHERE user_id = old_user_id
    ORDER BY id ASC; -- IDの順序を維持して採番させるため

    -- 4. hadbit_trees への移行
    -- item_id の紐付けが必要なため、名前等でマッチングして新旧IDを結合
    INSERT INTO public.hadbit_trees (item_id, user_id, parent_id, order_no)
    SELECT 
        new_item.id,
        new_user_uuid,
        parent_item.id, -- 新しい親IDをセット
        tree.order_no
    FROM public.habit_item_tree tree
    JOIN public.habit_items old_item ON tree.item_id = old_item.id
    JOIN public.hadbit_items new_item ON new_item.name = old_item.name AND new_item.user_id = new_user_uuid
    LEFT JOIN public.habit_items old_parent ON tree.parent_id = old_parent.id
    LEFT JOIN public.hadbit_items parent_item ON parent_item.name = old_parent.name AND parent_item.user_id = new_user_uuid
    WHERE old_item.user_id = old_user_id;

    -- 5. hadbit_logs への移行
    INSERT INTO public.hadbit_logs (
        user_id, item_id, done_at, updated_at, created_at, comment
    )
    SELECT 
        new_user_uuid,
        new_item.id,
        logs.done_at,
        logs.updated_at,
        logs.created_at,
        logs.comment
    FROM public.habit_logs logs
    JOIN public.habit_items old_item ON logs.item_id = old_item.id
    JOIN public.hadbit_items new_item ON new_item.name = old_item.name AND new_item.user_id = new_user_uuid
    WHERE logs.user_id = old_user_id;

    RAISE NOTICE 'コンバート完了: %', target_email;
END $$;

--parent_idがnullになったときに0に戻す
--update hadbit_trees
--set parent_id = 0
--  where user_id = '76b8d0ed-825d-43a6-a725-37e10c11015b'
--  and parent_id is null

```
# 履歴
- 2026/2/2
  - 歴の画面見やすくしてみた。
- 2026/2/1 
  - renderへデプロイ
- 2026/1/24 
  - FastAPIのBase作成完了
  - それベースでの作成開始