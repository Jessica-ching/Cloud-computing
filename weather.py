import streamlit as st
import requests
from datetime import datetime

API_KEY = 'CWA-1E665343-74C8-45A9-A44F-AD9617262FE4'
TARGET_LOCATION = '雲林縣'
DATA_ID = 'F-C0032-001'

st.set_page_config(
	page_title=f"{TARGET_LOCATION} 天氣報告", 
	layout="centered",
	initial_sidebar_state="collapsed"
)

st.title(f"☀️ {TARGET_LOCATION} 天氣預報")
st.caption(f"數據來源：中央氣象署 (CWA) | 資料集：{DATA_ID}")
st.markdown("---")

if not API_KEY:
	st.error("❌ 錯誤：找不到 CWA API 金鑰。")
else:
	base_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATA_ID}'
	params = {
		'Authorization': API_KEY,
		'format': 'JSON',
		'locationName': TARGET_LOCATION
	}

	try:
		with st.spinner(f"正在向 CWA API 請求 {TARGET_LOCATION} 資料..."):
			response = requests.get(base_url, params=params)
			response.raise_for_status() # 檢查 HTTP 錯誤
			data = response.json()

		locations = data.get('records', {}).get('location', [])

		if locations:
			yunlin_data = locations[0]
			st.success(f"✅ 成功取得 {yunlin_data['locationName']} 的天氣資料。")
			st.caption(f"資料更新於：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
            

			weather_elements = yunlin_data.get('weatherElement', [])
			wx_element = next((e for e in weather_elements if e['elementName'] == 'Wx'), None)
			min_temp_element = next((e for e in weather_elements if e['elementName'] == 'MinT'), None)
			max_temp_element = next((e for e in weather_elements if e['elementName'] == 'MaxT'), None)
            
			if wx_element and min_temp_element and max_temp_element:
				first_period = wx_element['time'][0]
				min_temp = min_temp_element['time'][0]['parameter']['parameterName']
				max_temp = max_temp_element['time'][0]['parameter']['parameterName']
                
				st.header("🕒 **未來時段預報**")
				st.info(f"預報區間：從 **{first_period['startTime']}** 至 **{first_period['endTime']}**")
				st.markdown("---")

				col1, col2, col3 = st.columns(3)
                
				with col1:
					st.metric(label="🌤️ 天氣狀況", 
						value=first_period['parameter']['parameterName'])

				with col2:
					st.metric(label="🌡️ 溫度範圍", 
						value=f"{min_temp} ~ {max_temp}°C")
                
				pop_element = next((e for e in weather_elements if e['elementName'] == 'PoP'), None)
				if pop_element:
					pop = pop_element['time'][0]['parameter']['parameterName']
					with col3:
						st.metric(label="☔ 降雨機率", 
							value=f"{pop}%")
                
				st.markdown("---")
                
			else:
				st.warning("⚠️ 成功取得資料，但找不到所需的天氣元素 (Wx, MinT, MaxT)。")

		else:
			st.error("⚠️ API 回傳的資料中找不到 'location' 資訊。請確認 API 狀態或金鑰是否有效。")
            
	except requests.exceptions.HTTPError as err:
		st.error(f"❌ HTTP 錯誤發生 (例如：金鑰錯誤或資料庫問題)。錯誤代碼：{err}")
	except requests.exceptions.RequestException as err:
		st.error(f"❌ 請求錯誤發生 (例如：網路連線問題)：{err}")
	except Exception as err:
		st.error(f"❌ 發生未知錯誤：{err}")