import requests
import flet as ft

# 気象庁APIのエンドポイント
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# 地域リストの取得
def fetch_area_list():
    response = requests.get(AREA_URL)
    if response.status_code == 200:
        data = response.json()
        areas = []
        # 'offices' 内から地域情報を取得
        offices = data.get('offices', {})
        for area_code, area_info in offices.items():
            name = area_info.get('name')
            if name:
                areas.append({"name": name, "code": area_code})
        print("Fetched areas:", areas)  # デバッグプリント追加
        return areas
    else:
        print("Failed to fetch area data")
        print(f"HTTP {response.status_code} - {response.text}")
        return []

# 天気情報の取得
def fetch_forecast(area_code):
    url = FORECAST_URL_TEMPLATE.format(area_code=area_code)
    print(f"Fetching forecast from URL: {url}")  # デバッグプリント追加
    response = requests.get(url)
    if response.status_code == 200:
        print("Fetched forecast data successfully:")
        forecast_data = response.json()
        print(forecast_data)  # レスポンスデータをデバッグプリント
        return forecast_data
    else:
        print("Failed to fetch forecast data")
        print(f"HTTP {response.status_code} - {response.text}")
    return {}

def display_weather_data(weather_output, forecast):
    weather_output.controls.clear()
    if forecast:
        try:
            timeseries = forecast[0]["timeSeries"]
            if timeseries:
                forecast_days = timeseries[0]["timeDefines"]
                areas_weather = timeseries[0]["areas"]
                temps_data = forecast[0]["timeSeries"][-1]["areas"]  # 温度データを取得

                for i, area_weather in enumerate(areas_weather):
                    area_name = area_weather.get("area", {}).get("name", "")
                    weather = area_weather.get("weathers", [])
                    
                    if i < len(temps_data):
                        temps = temps_data[i].get("temps", [])
                    else:
                        temps = []

                    if area_name and weather:
                        for j, date in enumerate(forecast_days):
                            date = date.split('T')[0]  # 日付のフォーマットを整える
                            max_temp = temps[j * 2 + 1] if len(temps) > j * 2 + 1 else 'N/A'
                            min_temp = temps[j * 2] if len(temps) > j * 2 else 'N/A'
                            # テンプレートを構築
                            weather_output.controls.append(
                                ft.Container(
                                    content=ft.Card(
                                        content=ft.Column(
                                            [
                                                ft.Text(area_name, size=18, weight=ft.FontWeight.BOLD),  # テキストサイズを調整
                                                ft.Text(date, size=18),  # テキストサイズを調整
                                                ft.Text(weather[j] if len(weather) > j else "データなし", size=16),  # テキストサイズを調整
                                                ft.Row(
                                                    [
                                                        ft.Text(f"最高: {max_temp}℃", size=16, color=ft.Colors.RED),  # テキストサイズを調整
                                                        ft.Text(f"最低: {min_temp}℃", size=16, color=ft.Colors.BLUE),  # テキストサイズを調整
                                                    ],
                                                    spacing=10,
                                                    alignment="center"
                                                )
                                            ],
                                            alignment="center",
                                            horizontal_alignment="center",
                                            spacing=5
                                        ),
                                        elevation=3
                                    ),
                                    padding=10,
                                    width=300,  # カードの幅を設定
                                    height=200  # カードの高さを設定
                                )
                            )
            else:
                weather_output.controls.append(ft.Text("天気データが取得できませんでした。", size=18))
        except Exception as ex:
            weather_output.controls.append(ft.Text(f"エラー: {ex}", size=18))
            print(f"Exception: {ex}")
    else:
        weather_output.controls.append(ft.Text("天気データが取得できませんでした。", size=18))

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT

    # ページ全体のサイズの設定
    page.window_full_screen = True  # ウィンドウを全画面表示に設定

    weather_output = ft.ListView(expand=True)  # スクロール可能なリストビュー

    # 地域リスト取得
    areas = fetch_area_list()

    def on_area_selected(e):
        area_code = e.control.data
        forecast = fetch_forecast(area_code)
        display_weather_data(weather_output, forecast)
        page.update()

    area_list = [
        ft.ListTile(
            title=ft.Text(area.get("name", "不明"), size=18),  # テキストサイズを調整
            data=area.get("code", "000000"),
            on_click=on_area_selected
        )
        for area in areas
    ]

    page.add(
        ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("地域を選択", size=24, weight=ft.FontWeight.BOLD),  # テキストサイズを調整
                            ft.ListView(
                                controls=area_list,
                                expand=True,
                            )
                        ],
                        spacing=15,
                        expand=True,
                    ),
                    width=300,  # コンテナの幅を設定
                    padding=15,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=10,
                    margin=10
                ),
                ft.Container(  # ft.Containerをラップしてpaddingを適用
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Text(
                                    "天気予報",
                                    size=28,  # タイトルのテキストサイズを調整
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                padding=10,
                                bgcolor=ft.Colors.BLUE,
                                border_radius=ft.border_radius.only(
                                    top_left=0,
                                    top_right=0,
                                    bottom_left=10,
                                    bottom_right=10
                                ),
                                width=1200  # 必要な幅を設定
                            ),
                            ft.Container(
                                weather_output,
                                expand=True,
                            )
                        ],
                        spacing=20,
                        expand=True,
                    ),
                    padding=15,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                    expand=True,
                    margin=10
                )
            ],
            expand=True
        )
    )

ft.app(target=main)