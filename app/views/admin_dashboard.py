import matplotlib

matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from app.models import Order, OrderItem, Product, Customer

def sales_dashboard(request):
    try:
        # Daily Sales Trend
        orders = Order.objects.filter(is_paid=True).values('date_order__date').annotate(total=Count('id'))
        if not orders:
            return render(request, 'app/dashboard.html', {'error': 'No data available'})
        df_orders = pd.DataFrame.from_records(orders)
        df_orders.rename(columns={'date_order__date': 'date_order'}, inplace=True)
        df_orders['date_order'] = pd.to_datetime(df_orders['date_order'])
        df_orders.set_index('date_order', inplace=True)
        df_grouped = df_orders['total'].resample('D').sum().fillna(0)

        plt.figure(figsize=(8, 4))
        plt.plot(df_grouped.index, df_grouped.values, marker='o', linestyle='-', color='g')
        plt.xlabel('Date')
        plt.ylabel('Total Orders')
        plt.title('Daily Order Trend')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        sales_chart = base64.b64encode(buffer.getvalue()).decode() if buffer.getvalue() else None
        buffer.close()
        plt.clf()

        items = OrderItem.objects.values('product__name', 'combo__name')
        items = items.annotate(total=Count('id')).order_by('-total')
        top_items = list(items[:4])
        others_count = sum([item['total'] for item in items[4:]])
        item_names = [item['product__name'] or item['combo__name'] for item in top_items] + (['Others'] if others_count > 0 else [])
        item_counts = [item['total'] for item in top_items] + ([others_count] if others_count > 0 else [])

        plt.figure(figsize=(8, 4))
        plt.pie(item_counts, labels=item_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        plt.title('Top 4 Most Purchased Items')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        top_items_chart = base64.b64encode(buffer.getvalue()).decode() if buffer.getvalue() else None
        buffer.close()
        plt.clf()

        customer_data = Order.objects.filter(is_paid=True).annotate(
            total_spent=Sum('orderitem__product__price')
        ).values('customer__name', 'total_spent').order_by('-total_spent')
        df_customers = pd.DataFrame.from_records(customer_data)

        if not df_customers.empty:
            customer_names = df_customers['customer__name'].fillna('Guest')
            customer_spent = df_customers['total_spent'].fillna(0)

            plt.figure(figsize=(8, 4))
            plt.bar(customer_names, customer_spent, color='orange')
            plt.xlabel('Customers')
            plt.ylabel('Total Amount Spent')
            plt.title('Customer Purchase Distribution')
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            customer_distribution_chart = base64.b64encode(buffer.getvalue()).decode() if buffer.getvalue() else None
            buffer.close()
            plt.clf()
        else:
            customer_distribution_chart = None


        category_data = OrderItem.objects.values('product__category__name').annotate(total_sold=Count('id')).order_by('-total_sold')
        df_category = pd.DataFrame.from_records(category_data)

        if not df_category.empty and 'product__category__name' in df_category.columns:
            df_category['product__category__name'] = df_category['product__category__name'].fillna('Unknown')
            category_names = df_category['product__category__name']
            category_sold = df_category['total_sold']

            plt.figure(figsize=(8, 4))
            plt.bar(category_names, category_sold, color='blue')
            plt.xlabel('Product Category')
            plt.ylabel('Total Products Sold')
            plt.title('Product Category Sales')
            plt.xticks(rotation=45)  # Xoay nhãn để dễ đọc
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            category_sales_chart = base64.b64encode(buffer.getvalue()).decode() if buffer.getvalue() else None
            buffer.close()
            plt.clf()
        else:
            category_sales_chart = None


        return render(request, 'app/dashboard.html', {
            'sales_chart': sales_chart,
            'top_items_chart': top_items_chart,
            'customer_distribution_chart': customer_distribution_chart,
            'category_sales_chart': category_sales_chart,  # Thêm chart mới
        })


    except Exception as e:
        print('❌ Lỗi xảy ra:', e)
        return render(request, 'app/dashboard.html', {'error': str(e)})
