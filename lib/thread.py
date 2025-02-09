import threading
import queue
import time

# Создаем очередь для общения между потоками
data_queue = queue.Queue()

# Функция для дочернего потока 1
def thread1(queue):
    for i in range(5):
        time.sleep(1)
        message = f"Thread 1: Message {i}"
        queue.put(message)  # Отправляем сообщение в очередь
    queue.put("Thread 1 finished")

# Функция для дочернего потока 2
def thread2(queue):
    for i in range(3):
        time.sleep(2)
        message = f"Thread 2: Message {i}"
        queue.put(message)  # Отправляем сообщение в очередь
    queue.put("Thread 2 finished")

# Главный поток
if __name__ == "__main__":
    print("Main thread started")

    # Создаем и запускаем дочерние потоки
    t1 = threading.Thread(target=thread1, args=(data_queue,))
    t2 = threading.Thread(target=thread2, args=(data_queue,))
    t1.start()
    t2.start()

    # Читаем сообщения из очереди в главном потоке
    while True:
        try:
            message = data_queue.get(timeout=1)  # Ждем сообщение с таймаутом
            print(f"Main thread received: {message}")
            if "finished" in message:
                # Если получено сообщение о завершении, проверяем статус потоков
                if not t1.is_alive() and not t2.is_alive():
                    break
        except queue.Empty:
            continue

    print("Main thread finished")
