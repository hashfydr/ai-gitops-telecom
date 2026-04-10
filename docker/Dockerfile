FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Bundle the entire pipeline
COPY parse_data.py train_model.py gitops_controller.py .
# Create a dummy CSV to prevent initial crash
RUN echo "flow_id,lost_packets,delay_sum_ns,jitter_ns\n1,0,100,5" > flow_metrics.csv
CMD ["python", "-u", "gitops_controller.py"]
