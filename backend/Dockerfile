FROM continuumio/miniconda3:24.7.1-0

WORKDIR /app

# Системные зависимости для Brian2 C++ генерации
RUN apt-get update && apt-get install -y \
    gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

# Brian2 через conda (требует компилятор)
RUN conda install -y -c conda-forge \
    brian2=2.7.1 \
    python=3.11 \
    && conda clean -afy

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY . .

# Создать директорию для результатов
RUN mkdir -p /app/data/results

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
