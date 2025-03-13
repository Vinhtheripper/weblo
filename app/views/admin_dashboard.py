import matplotlib

matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.db.models import Count
from app.models import Order


def sales_dashboard(request):
    try:
        # 🛠️ Lấy dữ liệu từ DB
        orders = Order.objects.values('date_order__date').annotate(total=Count('id'))

        # 🛠️ Debug: Kiểm tra dữ liệu lấy được
        print("Orders:", list(orders))

        if not orders:  # Nếu không có dữ liệu, trả về trang trống
            return render(request, 'app/sales_chart.html', {'sales_chart': None})

        # Chuyển dữ liệu thành DataFrame
        df = pd.DataFrame.from_records(orders)

        # 🛠️ Đổi tên cột từ 'date_order__date' thành 'date_order'
        df.rename(columns={'date_order__date': 'date_order'}, inplace=True)

        # Chuyển cột thành datetime
        df['date_order'] = pd.to_datetime(df['date_order'])

        # 🛠️ Nhóm dữ liệu theo ngày
        df.set_index('date_order', inplace=True)
        df_grouped = df['total'].resample('D').sum().fillna(0)

        # 🛠️ Vẽ biểu đồ
        plt.figure(figsize=(8, 4))
        plt.plot(df_grouped.index, df_grouped.values, marker='o', linestyle='-', color='g')
        plt.xlabel('Date')
        plt.ylabel('Total Orders')
        plt.title('Daily Order Trend')
        plt.xticks(rotation=45)

        # Chuyển ảnh thành base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        sales_chart = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        return render(request, 'app/dashboard.html', {'sales_chart': sales_chart})

    except Exception as e:
        print("❌ Lỗi xảy ra:", e)
        return render(request, 'app/dashboard.html', {'sales_chart': None, 'error': str(e)})
