# snippet generator

> **Warning**
> このアプリケーションは、信頼できるファイルに対して実行されることを意図しています。
> 信頼できないファイルに対して実行した場合、セキュリティ上のリスクがある場合があります。

## 特徴
 - 様々な言語に対応
   - 言語特有の機能や記法に依存せずにメタデータを表現
 - 様々なエディタに対応

## ファイル形式
ファイルは header, variables, body セクションに分かれています。これらはこの順番に登場しなくてはいけません。なお、`VARIABLES` セクションは登場しなくてもよいです。

### 例
```c++
// HEADER
// name: greeting
// prefix: greeting
// description: greeting from the language!

// VARIABLES
/*
 *     _name:
 * _language: |"c", "cpp"|
 *  _version: 19
 */

// BODY
printf("Hello, %s! This is %s_version.", "_name", _language);
```

### header
`HEADER` という文字が登場した行から、次のセクションまでの行が header セクションに属します。
区切り文字は `header-signature` 変数で変更できます。
key と value は次のような正規表現によって、行ごとに取り出されます: `([a-zA-Z0-9_-]+):? +(.*)`
区切り文字の正規表現 `:? +` は `header-separator` 変数で変更できます。

### variables
`VARIABLES` という文字が登場した行から、次のセクションまでの行が header セクションに属します。
区切り文字は `variables-signature` 変数で変更できます。
key と value は次のような正規表現によって、行ごとに取り出されます: `([a-zA-Z0-9_-]+):? +(.*)`
区切り文字の正規表現 `:? +` は `variable-separator` 変数で変更できます。

### body
`BODY` という文字が登場した行から header セクションに属します。
ここの内容は、そのまま body となります。

### 非対応の機能
 - ネストされた変数
 - 変数に対する description

## 各種形式
### vscode extension
> TODO: 書く

## TODO
 - テストを書く
 - 別の snippet 形式にも対応
   - Visual Studio
   - vim
   - emacs(yasnippet)
