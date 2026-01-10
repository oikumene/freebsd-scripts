# What is it?

This script retrieves weather data from Japanese Metrological
Agency, and tidy up for waybar custom module.

So, the rest of the document will be written in Japanese.

# 概要

気象庁が公開しているデータを取ってきて、
指定した地点のアメダスデータから
waybar で表示するための情報に加工します。

気象庁のサーバーに負荷をかけすぎないために、
データを取ってきて加工するこのスクリプトと、
waybar のカスタムモジュールを分けています。

だいたいの動かし方としては、以下のようになります。

1. 一時間に一回このスクリプトを動かして weather.json を生成する
2. waybar の config に、weather.json の内容を10分～20分に一度
   読み込むように記述する

weather.json の内容をどうとってくるかについては、
複数のホストで使いまわしたい場合は web server に置いてそれを
fetch する、
利用するホストが一台だけならどこか適当なディレクトリに置いて
それを cat するということになろうかと思います。

# 動かし方

## 準備

パッケージから、pyXXX-requests と python3
をインストールしておいてください。
```
# pkg install python3
# pkg install py311-requests
```

データを置くディレクトリを決めます。
web server からサービスするなら /www/data/weather
とかになるでしょうし、
個人で自分だけで動かすなら ~/.config/waybar あたりでよいでしょう。
ここから先の説明は、
このディレクトリがカレントディレクトリという前提で進めます。

アメダスの地点情報が載っている amedastable.json を取ってきます。
これはそう変わるものではないので、都度取らないようにしています。
```
% fetch https://www.jma.go.jp/bosai/amedas/const/amedastable.json
```

データをとりたいアメダスの漢字名をスクリプト冒頭の
amedas_points というリストに記述します。
最初に書かれた地点が常に waybar に表示されます。
全ての地点のもう少し詳しいデータが tooltip に表示されます。
存在しない漢字名（例えば「南野」）
を書くとエラーになりますので気をつけてください。
サンプルとして以下の3都市を記述しています。
```
amedas_points = ["東京", "札幌", "那覇"]
```

## cron の設定

cron で一時間に一回動かします。
気象庁のサーバーへの負荷を分散させるため、
きりのよくない、この例以外の時刻を設定してください。

nobody ユーザーで動かす場合、/etc/cron.d/www とかに
```
0  *  *  *  *  nobody  -n cd /path/to/dir && /path/to/dir/generate-weather-data.py
```

自分の crontab で動かす場合は
```
0  *  *  *  *  -n cd /path/to/dir && /path/to/dir/generate-weather-data.py
```

これで一時間毎に weather.json が生成されるはずです。

## waybar の設定

~/.config/waybar/config の modules-left か modules-center か
modules-right かに custom/weather を足します。
```
  "modules-left": ["custom/weather"],
```
そうして下の方に、モジュールの設定を記述します。
web server に置いたのを取ってくる場合は
```
    "custom/weather": {
        "return-type": "json",
        "exec": "fetch -o - http://example.jp/data/weather/weather.json",
        "interval": 900
    }
```

ローカルのディレクトリに置いたのを読む場合は
```
    "custom/weather": {
        "return-type": "json",
        "exec": "cat ~/.config/waybar/weather.json",
        "interval": 900
```
