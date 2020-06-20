"""
Title: 엔지니어에게 맞는 케라스 소개
Author: [fchollet](https://twitter.com/fchollet)
Date created: 2020/04/01
Last modified: 2020/04/28
Description: 케라스로 실전 머신러닝 솔루션을 만들기 위해 알아야 할 모든 것.
"""

"""
## 설정
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras

"""
## 소개

케라스로 제품에 딥러닝을 적용하고 싶은 머신러닝 엔지니어인가요? 이 가이드에서 케라스 API의 핵심 부분을 소개하겠습니다.

이 가이드에서 다음 내용을 배울 수 있습니다:

- 모델을 훈련하기 전에 데이터를 준비하는 방법(넘파이 배열이나 `tf.data.Dataset` 객체로 변환합니다).
- 데이터 전처리 방법. 예를 들면 특성 정규화나 어휘 사전 구축.
- 케라스 함수형 API로 데이터에서 예측을 만드는 모델 구축 방법.
- 케라스의 기본 `fit()` 메서드로 체크포인팅(checkpointing), 성능 지표 모니터링, 내결함성(fault tolerance)을 고려한 모델 훈련 방법.
- 테스트 데이터에서 모델 평가하고 새로운 데이터에서 모델을 사용해 추론하는 방법.
- GAN과 같은 모델을 만들기 위해 `fit()` 메서드를 커스터마이징하는 방법.
- 여러 개의 GPU를 사용해 훈련 속도를 높이는 방법.
- 하이퍼파라미터를 튜닝하여 모델의 성능을 높이는 방법.

이 문서 끝에 다음 주제에 대한 엔드-투-엔드 예제 링크를 소개하겠습니다:

- 이미지 분류
- 텍스트 분류
- 신용 카드 부정 거래 감지


"""

"""
## 데이터 적재와 전처리

신경망은 텍스트 파일, JPEG 이미지 파일, CSV 파일 같은 원시 데이터를 그대로 처리하지 않습니다.
신경망은 **벡터화**되거나 **표준화**된 표현을 처리합니다.

- 텍스트 파일을 문자열 텐서로 읽어 단어로 분리합니다. 마지막에 단어를 정수 텐서로 인덱싱하고 변환합니다.
- 이미지를 읽어 정수 텐서로 디코딩합니다. 그다음 부동 소수로 변환하고 (보통 0에서 1사이) 작은 값으로 정규화합니다.
- CSV 데이터를 파싱하여 정수 특성은 부동 소수 텐서로 변환하고, 범주형 특성은 정수 텐서로 인덱싱하고 변환합니다.
그다음 일반적으로 각 특성을 평균 0, 단위 분산으로 정규화합니다.

먼저 데이터를 적재해 보죠.

## 데이터 적재

케라스 모델은 세 종류의 입력을 받습니다:

- **넘파이(NumPy) 배열**. 사이킷런(Scikit-Learn)이나 다른 파이썬 라이브러리와 비슷합니다.
데이터 크기가 메모리에 맞을 때 좋습니다.
- **[텐서플로 `Dataset` 객체](https://www.tensorflow.org/guide/data)**.
데이터가 메모리보다 커서 디스크나 분산 파일 시스템에서 스트림으로 읽어야할 때 적합한 고성능 방식입니다.
- **파이썬 제너레이터(generator)**. 배치 데이터를 만듭니다(`keras.utils.Sequence` 클래스의
사용자 정의 서브클래스와 비슷합니다).

모델을 훈련하기 전에 이런 포맷 중에 하나로 데이터를 준비해야 합니다.
데이터셋이 크고 GPU에서 훈련한다면 `Dataset` 객체를 사용하는 것이 좋습니다.
다음 같이 성능에 아주 중요한 기능을 제공하기 때문입니다:

- GPU가 바쁠 때 CPU에서 데이터를 비동기적으로 전처리하고 큐에 버퍼링합니다.
- GPU 메모리에 데이터를 프리페치(prefetch)하여 GPU에서 이전 배치에 대한 처리가 끝나는대로 즉시 사용할 수 있습니다.
이를 통해 GPU를 최대로 활용할 수 있습니다.

케라스는 디스크에 있는 원시 데이터를 `Dataset`으로 변환해 주는
여러 유틸리티를 제공합니다(**옮긴이_** 아래 함수는 아직 tf-nightly 패키지에서만 제공합니다):

- `tf.keras.preprocessing.image_dataset_from_directory`는 클래스별로 폴더에 나뉘어 있는 이미지 파일을
레이블된 이미지 텐서 데이터셋으로 변환합니다.
- `tf.keras.preprocessing.text_dataset_from_directory`는 텍스트 파일에 대해 동일한 작업을 수행합니다.

또한 텐서플로의 `tf.data`는 CSV 파일에서 정형화된 데이터를 로드하는
`tf.data.experimental.make_csv_dataset`와 같은 유틸리티를 제공합니다.

**예제: 디스크에 있는 이미지 파일에서 레이블된 데이터셋 만들기**

다음처럼 클래스별로 각기 다른 폴더에 이미지 파일이 들어 있다고 가정해 보죠:

```
main_directory/
...class_a/
......a_image_1.jpg
......a_image_2.jpg
...class_b/
......b_image_1.jpg
......b_image_2.jpg
```

그럼 다음처럼 쓸 수 있습니다:

```python
# 데이터셋을 만듭니다.
dataset = keras.preprocessing.image_dataset_from_directory(
  'path/to/main_directory', batch_size=64, image_size=(200, 200))

# 예시를 위해 데이터셋의 배치를 순회합니다.
for data, labels in dataset:
   print(data.shape)  # (64, 200, 200, 3)
   print(data.dtype)  # float32
   print(labels.shape)  # (64,)
   print(labels.dtype)  # int32
```

샘플의 레이블은 폴더의 알파벳 순서대로 매겨집니다.
매개변수를 사용해 명시적으로 지정할 수도 있습니다.
예를 들어 `class_names=['class_a', 'class_b']`라고 쓸 경우 다
클래스 레이블 `0`은 `class_a`가 되고 `1`은 `class_b`가 됩니.

**예제: 디스크에 있는 텍스트 파일에서 레이블된 데이터셋 만들기**

텍스트도 비슷합니다. 클래스별로 다른 폴더에 `.txt` 파일이 있다면 다음과 같이 쓸 수 있습니다:

```python
dataset = keras.preprocessing.text_dataset_from_directory(
  'path/to/main_directory', batch_size=64)

# 예시를 위해 데이터셋의 배치를 순회합니다.
for data, labels in dataset:
   print(data.shape)  # (64,)
   print(data.dtype)  # string
   print(labels.shape)  # (64,)
   print(labels.dtype)  # int32
```



"""

"""
## 케라스를 사용한 데이터 전처리

데이터가 문자열/정수/실수 넘파이 배열이거나
문자열/정수/실수 텐서의 배치를 반환하는 `Dataset` 객체(또는 파이썬 제너레이터)로 준비되었다면
이제 데이터를 **전처리**할 차례입니다. 이 과정은 다음과 같은 작업을 의미합니다:

- 문자열 데이터를 토큰으로 나누고 인덱싱합니다.
- 특성을 정규화합니다.
- 데이터를 작은 값으로 스케일을 조정합니다(일반적으로 신경망의 입력은 0에 가까워야 합니다.
평균이 0이고 분산이 1이거나 `[0, 1]` 범위의 데이터를 기대합니다).

### 이상적인 머신러닝 모델은 엔드-투-엔드 모델입니다

일반적으로 가능하면 데이터 전처리를 별도의 파이프라인으로 만들지 않고 **모델의 일부**가 되도록 해야 합니다.
별도의 데이터 전처리 파이프라인은 모델을 제품에 투입할 때 이식하기 어렵게 만들기 때문입니다.
텍스트 처리를 하는 모델을 생각해 보죠.
이 모델은 특별한 토큰화 알고리즘과 어휘 사전 인덱스를 사용합니다.
이 모델을 모바일 앱이나 자바스크립트 앱에 적용할 때 해당 언어로 동일한 전처리 과정을 다시 구현해야 합니다.
이는 매우 위험한 작업입니다.
원래 파이프라인과 다시 만든 파이프라인 사이에 작은 차이가 모델을 완전히 망가뜨리거나
성능을 크게 낮출 수 있기 때문입니다.

전처리를 포함한 엔드-투-엔드(end-to-end) 모델로 만들 수 있다면 훨씬 간단합니다.
**이상적인 모델은 가능한 원시 데이터에 가까운 입력을 기대해야 합니다.
이미지 모델은 `[0, 255]` 사이의 RGB 픽셀 값을 기대합니다.
텍스트 모델은 `utf-8` 문자열을 기대합니다.**
따라서 이 모델을 사용하는 애플리케이션은 전처리 파이프라인에 대해 신경쓸 필요가 없습니다.

### 케라스 전처리 층 사용하기

케라스에서는 **전처리 층**으로 모델에서 데이터 전처리를 수행합니다.
다음과 같은 기능을 제공합니다:

- `TextVectorization` 층으로 텍스트 원시 문자열을 벡터화합니다.
- `Normalization` 층으로 특성을 정규화합니다.
- 이미지 스케일 조정, 자르기, 데이터 증식을 수행합니다.

케라스 전처리 층을 사용할 때 가장 큰 장점은 훈련하는 중간이나 훈련이 끝난 후에
이 층을 **모델에 직접 포함하여** 모델의 이식성을 높일 수 있다는 점입니다.

일부 전처리 층은 상태를 가집니다:

- `TextVectorization`는 정수 인덱스로 매핑된 단어나 토큰을 저장합니다.
- `Normalization`는 특성의 평균과 분산을 저장합니다.

훈련 데이터의 샘플(또는 전체 데이터)을 사용해 `layer.adapt(data)`를 호출하면 전처리 층의 상태가 반환됩니다.


**예제: 문자열을 정수 단어 인덱스의 시퀀스로 변환하기**


"""

from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

# dtype이 `string`인 예제 훈련 데이터.
training_data = np.array([["This is the 1st sample."], ["And here's the 2nd sample."]])

# TextVectorization 층 객체를 만듭니다.
# 정수 토큰 인덱스 또는 토큰의 밀집 표현(예를 들어 멀티-핫(multi-hot)이나 TF-IDF)을 반환할 수 있습니다.
# 텍스트 표준화와 텍스트 분할 알고리즘을 완전히 커스터마이징할 수 있습니다.
vectorizer = TextVectorization(output_mode="int")

# 배열이나 데이터셋에 대해 `adapt` 메서드를 호출하면 어휘 인덱스를 생성합니다.
# 이 어휘 인덱스는 새로운 데이터를 처리할 때 재사용됩니다.
vectorizer.adapt(training_data)

# `adapt`를 호출하고 나면 이 메서드가 데이터에서 보았던 n-그램(n-gram)을 인코딩할 수 있습니다.
# 본적 없는 n-그램은 OOB(out-of-vocabulary) 토큰으로 인코딩됩니다.
integer_data = vectorizer(training_data)
print(integer_data)

"""
**예제: 문자열을 원-핫 인코딩된 바이그램(bigram) 시퀀스로 변환하기**
"""

from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

# dtype이 `string`인 예제 훈련 데이터.
training_data = np.array([["This is the 1st sample."], ["And here's the 2nd sample."]])

# TextVectorization 층 객체를 만듭니다.
# 정수 토큰 인덱스 또는 토큰의 밀집 표현(예를 들어 멀티-핫(multi-hot)이나 TF-IDF)을 반환할 수 있습니다.
# 텍스트 표준화와 텍스트 분할 알고리즘을 완전히 커스터마이징할 수 있습니다.
vectorizer = TextVectorization(output_mode="binary", ngrams=2)

# 배열이나 데이터셋에 대해 `adapt` 메서드를 호출하면 어휘 인덱스를 생성합니다.
# 이 어휘 인덱스는 새로운 데이터를 처리할 때 재사용됩니다.
vectorizer.adapt(training_data)

# `adapt`를 호출하고 나면 이 메서드가 데이터에서 보았던 n-그램(n-gram)을 인코딩할 수 있습니다.
# 본적 없는 n-그램은 OOB(out-of-vocabulary) 토큰으로 인코딩됩니다.
integer_data = vectorizer(training_data)
print(integer_data)

"""
**예제: 특성 정규화**

"""

from tensorflow.keras.layers.experimental.preprocessing import Normalization

# [0, 255] 사이의 값을 가진 예제 이미지 데이터
training_data = np.random.randint(0, 256, size=(64, 200, 200, 3)).astype("float32")

normalizer = Normalization(axis=-1)
normalizer.adapt(training_data)

normalized_data = normalizer(training_data)
print("분산: %.4f" % np.var(normalized_data))
print("평균: %.4f" % np.mean(normalized_data))

"""
**예제: 이미지 스케일 조정과 자르기**

`Rescaling` 층과 `CenterCrop` 층은 상태가 없습니다.
따라서 `adapt()` 메서드를 호출할 필요가 없습니다.
"""

from tensorflow.keras.layers.experimental.preprocessing import CenterCrop
from tensorflow.keras.layers.experimental.preprocessing import Rescaling

# [0, 255] 사이의 값을 가진 예제 이미지 데이터
training_data = np.random.randint(0, 256, size=(64, 200, 200, 3)).astype("float32")

cropper = CenterCrop(height=150, width=150)
scaler = Rescaling(scale=1.0 / 255)

output_data = scaler(cropper(training_data))
print("크기:", output_data.shape)
print("최소:", np.min(output_data))
print("최대:", np.max(output_data))

"""
## 케라스 함수형 API로 모델을 만들기

"층"은 (위의 스케일 조정이나 자르기처럼) 단순한 입력-출력 변환입니다.
예를 들어 다음은 입력을 16차원 특성 공간으로 매핑하는 선형 변환 층입니다:

```python
dense = keras.layers.Dense(units=16)
```

"모델"은 층의 유향 비순환 그래프(directed acyclic graph)입니다.
모델을 여러 하위 층을 감싸고 있고 데이터에 노출되어 훈련할 수 있는 "큰 층"으로 생각할 수 있습니다.

케라스 모델을 만들 때 가장 강력하고 널리 사용하는 방법은 함수형 API(Functional API)입니다.
함수형 API로 모델을 만들려면 먼저 입력의 크기(그리고 선택적으로 dtype)를 지정해야 합니다.
입력 차원이 변경될 수 있으면 `None`으로 지정합니다.
예를 들어 200x200 RGB 이미지의 입력 크기는 `(200, 200, 3)`로 지정하고
임의의 크기를 가진 RGB 이미지의 입력 크기는 `(None, None, 3)`으로 지정합니다.
"""

# 임의의 크기를 가진 RGB 이미지 입력을 사용한다고 가정해 보죠.
inputs = keras.Input(shape=(None, None, 3))

"""
입력을 정의한 후 이 입력에서 최종 출력까지 층 변환을 연결합니다:
"""

from tensorflow.keras import layers

# 150x150 중앙 부분을 오려냅니다.
x = CenterCrop(height=150, width=150)(inputs)
# [0, 1] 사이로 이미지 스케일을 조정합니다.
x = Rescaling(scale=1.0 / 255)(x)

# 합성곱과 풀링 층을 적용합니다.
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)
x = layers.MaxPooling2D(pool_size=(3, 3))(x)
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)
x = layers.MaxPooling2D(pool_size=(3, 3))(x)
x = layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu")(x)

# 전역 풀링 층을 적용하여 일렬로 펼친 특성 벡터를 얻습니다.
x = layers.GlobalAveragePooling2D()(x)

# 그 다음에 분류를 위해 밀집 층을 추가합니다.
num_classes = 10
outputs = layers.Dense(num_classes, activation="softmax")(x)

"""
입력을 출력으로 바꾸는 층의 유향 비순환 그래프를 정의하고 나서 `Model` 객체를 만듭니다:
"""

model = keras.Model(inputs=inputs, outputs=outputs)

"""
이 모델은 기본적으로 큰 층처럼 동작합니다. 다음처럼 배치 데이터에서 모델을 호출할 수 있습니다:
"""

data = np.random.randint(0, 256, size=(64, 200, 200, 3)).astype("float32")
processed_data = model(data)
print(processed_data.shape)

"""
모델의 각 단계에서 데이터가 어떻게 변환되는지 요약 정보를 출력하면 디버깅에 도움이 됩니다.

각 층에 표시되는 출력 크기는 **배치 크기**를 포함합니다.
배치 크기가 `None`이면 이 모델이 어떤 크기의 배치도 처리할 수 있다는 의미입니다.
"""

model.summary()

"""
함수형 API는 여러 개의 입력(예를 들어 이미지와 메타데이터)이나
여러 개의 출력(예를 들어 이미지 클래스와 클릭 확률을 예측)을 사용하는 모델도 쉽게 만들 수 있습니다.
이에 대해 더 자세한 정보는 [함수형 API 가이드](/guides/functional_api/)를 참고하세요.
"""

"""
## `fit()`으로 모델 훈련하기

지금까지 다음 내용을 배웠습니다:

- 데이터를 준비하는 방법(예를 들어 넘파이 배열이나 `tf.data.Dataset` 객체)
- 데이터를 처리할 모델을 만드는 방법

다음 단계는 데이터에서 모델을 훈련하는 것입니다.
`Model` 클래스는 `fit()` 메서드에서 훈련을 반복합니다.
이 메서드는 `Dataset` 객체, 배치 데이터를 반환하는 파이썬 제너레이터, 넘파이 배열을 받습니다.

`fit()` 메서드를 호출하기 전에 옵티마이저와 손실 함수를 지정해야 합니다(여러분이
이런 개념을 이미 알고 있다고 가정하겠습니다). 이것이 `compile()` 단계입니다:

```python
model.compile(optimizer=keras.optimizers.RMSprop(learning_rate=1e-3),
              loss=keras.losses.CategoricalCrossentropy())
```

손실 함수와 옵티마이저는 문자열로 지정할 수 있습니다(기본 생성자 매개변수가 사용됩니다):


```python
model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
```

모델이 컴파일되면 데이터에서 "훈련"을 시작할 수 있습니다.
다음은 넘파이 데이터를 사용해 모델을 훈련하는 예입니다:

```python
model.fit(numpy_array_of_samples, numpy_array_of_labels,
          batch_size=32, epochs=10)
```

데이터 외에도 두 개의 핵심 매개변수를 지정해야 합니다.
`batch_size`와 에포크 횟수(데이터를 반복할 횟수)입니다.
여기에서는 데이터를 32개 샘플씩 배치로 나누어 사용하고 훈련하는 동안 전체 데이터에 대해 10번 반복합니다.

다음은 데이터셋을 사용해 모델을 훈련하는 예입니다:

```python
model.fit(dataset_of_samples_and_labels, epochs=10)
```

데이터셋은 배치 데이터를 반환하기 때문에 배치 크기를 지정할 필요가 없습니다.

MNIST 숫자를 분류하는 작은 예제 모델을 만들어 보겠습니다:
"""

# 넘파이 배열로 데이터를 가져옵니다.
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

# 간단한 모델을 만듭니다.
inputs = keras.Input(shape=(28, 28))
x = layers.experimental.preprocessing.Rescaling(1.0 / 255)(inputs)
x = layers.Flatten()(x)
x = layers.Dense(128, activation="relu")(x)
x = layers.Dense(128, activation="relu")(x)
outputs = layers.Dense(10, activation="softmax")(x)
model = keras.Model(inputs, outputs)
model.summary()

# 모델을 컴파일합니다.
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy")

# 넘파이 데이터에서 1 에포크 동안 모델을 훈련합니다.
batch_size = 64
print("넘파이 데이터에서 훈련하기")
history = model.fit(x_train, y_train, batch_size=batch_size, epochs=1)

# 데이터셋을 사용해 1 에포크 동안 모델을 훈련합니다.
dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(batch_size)
print("데이터셋에서 훈련하기")
history = model.fit(dataset, epochs=1)

"""
`fit()` 메서드는 훈련 동안 발생하는 정보를 기록한 "history" 객체를 반환합니다.
`history.history` 딕셔너리는 에포크 순서대로 측정 값을 담고 있습니다(여기에서는
손실 하나와 에포크 횟수가 1이므로 하나의 스칼라 값만 담고 있습니다):
"""

print(history.history)

"""
`fit()` 메서드를 사용하는 자세한 방법은
[케라스 내장 메서드를 사용한 훈련과 평가 가이드](/guides/training_with_built_in_methods/)를
참고하세요.
"""

"""
### 성능 지표 기록하기

모델을 훈련하면서 분류 정확도, 정밀도, 재현율, AUC와 같은 지표를 기록할 필요가 있습니다.
이외에도 훈련 데이터에 대한 지표뿐만 아니라 검증 세트에 대한 모니터링도 필요합니다.

**성능 지표 모니터링**

다음처럼 `compile()` 메서드에 측정 지표의 객체 리스트를 전달할 수 있습니다:


"""

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
)
history = model.fit(dataset, epochs=1)

"""

**`fit()` 메서드에 검증 데이터 전달하기**

`fit()` 메서드에 검증 데이터를 전달하여 검증 손실과 성능 지표를 모니터링할 수 있습니다.
측정 값은 매 에포크 끝에서 출력됩니다.

"""

val_dataset = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(batch_size)
history = model.fit(dataset, epochs=1, validation_data=val_dataset)

"""
### 콜백을 사용해 체크포인트와 다른 여러 작업 수행하기

훈련이 몇 분 이상 지속되면 훈련하는 동안 일정 간격으로 모델을 저장하는 것이 좋습니다.
그러면 훈련 과정에 문제가 생겼을 때 저장된 모델을 사용해 훈련을 다시 시작할 수
있습니다(다중 워커(multi-worker) 분산 훈련일 경우
여러 워커 중 하나가 어느 순간 장애를 일으킬 수 있기 때문에 이 설정이 중요합니다).

케라스의 중요한 기능 중 하나는 `fit()` 메서드에 설정할 수 있는 **콜백**(callback)입니다.
콜백은 훈련하는 동안 각기 다른 지점에서 모델이 호출하는 객체입니다. 예를 들면 다음과 같습니다:

- 각 배치의 시작과 끝에서
- 각 에포크의 시작과 끝에서

콜백을 사용하면 모델의 훈련을 완전하게 제어할 수 있습니다.

콜백을 사용해 일정한 간격으로 모델을 저장할 수 있습니다. 다음이 간단한 예입니다.
에포크가 종료될 때마다 모델을 저장하도록 `ModelCheckpoint` 콜백을 설정하고
파일 이름에 현재 에포크를 포함시켰습니다.

```python
callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath='path/to/my/model_{epoch}',
        save_freq='epoch')
]
model.fit(dataset, epochs=2, callbacks=callbacks)
```
"""

"""
또 콜백을 사용해 일정한 간격으로 옵티마이저의 학습률을 바꾸거나,
슬랙 봇에 측정 값을 보내거나, 훈련이 완료됐을 때 이메일 알림을 보낼 수 있습니다.

사용할 수 있는 콜백과 사용자 정의 콜백을 작성하는 자세한 방법은
[콜백 API 문서](/api/callbacks/)와
[사용자 정의 콜백 가이드](/guides/writing_your_own_callbacks/)를 참고하세요.
"""

"""
### 텐서보드로 훈련 과정 모니터링하기

케라스 진행 표시줄(progress bar)은 손실과 측정 지표가 시간에 따라
어떻게 변하는지 모니터링하기 편리한 도구는 아닙니다.
더 나은 방법은 실시간 측정 값을 그래프로 (그리고 다른 여러 정보를) 보여주는 웹 애플리케이션인
[텐서보드](https://www.tensorflow.org/tensorboard)(TensorBoard)입니다.

`fit()` 메서드에 텐서보드를 사용하려면 간단하게 텐서보드 로그 저장
디렉토리를 설정한 `keras.callbacks.TensorBoard` 콜백을 전달하면 됩니다:


```python
callbacks = [
    keras.callbacks.TensorBoard(log_dir='./logs')
]
model.fit(dataset, epochs=2, callbacks=callbacks)
```

그다음 텐서보드 프로그램을 실행하여 브라우저에서 저장된 로그를 모니터링할 수 있습니다:

```
tensorboard --logdir=./logs
```

또한 주피터 노트북이나 코랩 노트북에서 모델을 훈련할 때 인라인으로 텐서보드 탭을 실행할 수 있습니다.
[자세한 정보는 여기를 참고하세요](https://www.tensorflow.org/tensorboard/tensorboard_in_notebooks).
"""

"""
### `fit()` 메서드 실행 후 테스트 성능을 평가하고 새로운 데이터에 대해 예측 만들기

모델 훈련을 마치면 `evaluate()` 메서드로 새로운 데이터에 대한 손실과 측정 지표를 평가할 수 있습니다:
"""

loss, acc = model.evaluate(val_dataset)  # 손실과 측정 값을 반환합니다.
print("손실: %.2f" % loss)
print("정확도: %.2f" % acc)

"""
`predict()` 메서드로 넘파이 배열로 예측(모델에 있는 출력층의 활성화 값)을 만들 수도 있습니다:
"""

predictions = model.predict(val_dataset)
print(predictions.shape)

"""
## Using `fit()` with a custom training step

By default, `fit()` is configured for **supervised learning**. If you need a different
 kind of training loop (for instance, a GAN training loop), you
can provide your own implementation of the `Model.train_step()` method. This is the
 method that is repeatedly called during `fit()`.

Metrics, callbacks, etc. will work as usual.

Here's a simple example that reimplements what `fit()` normally does:

```python
class CustomModel(keras.Model):
  def train_step(self, data):
    # Unpack the data. Its structure depends on your model and
    # on what you pass to `fit()`.
    x, y = data
    with tf.GradientTape() as tape:
      y_pred = self(x, training=True)  # Forward pass
      # Compute the loss value
      # (the loss function is configured in `compile()`)
      loss = self.compiled_loss(y, y_pred,
                                regularization_losses=self.losses)
    # Compute gradients
    trainable_vars = self.trainable_variables
    gradients = tape.gradient(loss, trainable_vars)
    # Update weights
    self.optimizer.apply_gradients(zip(gradients, trainable_vars))
    # Update metrics (includes the metric that tracks the loss)
    self.compiled_metrics.update_state(y, y_pred)
    # Return a dict mapping metric names to current value
    return {m.name: m.result() for m in self.metrics}

# Construct and compile an instance of CustomModel
inputs = keras.Input(shape=(32,))
outputs = keras.layers.Dense(1)(inputs)
model = CustomModel(inputs, outputs)
model.compile(optimizer='adam', loss='mse', metrics=[...])

# Just use `fit` as usual
model.fit(dataset, epochs=3, callbacks=...)
```

For a detailed overview of how you customize the built-in training & evaluation loops,
 see the guide:
["Customizing what happens in `fit()`"](/guides/customizing_what_happens_in_fit/).
"""

"""
## Debugging your model with eager execution

If you write custom training steps or custom layers, you will need to debug them. The
debugging experience is an integral part of a framework: with Keras, the debugging
 workflow is designed with the user in mind.

By default, your Keras models are compiled to highly-optimized computation graphs that
deliver fast execution times. That means that the Python code you write (e.g. in a
custom `train_step`) is not the code you are actually executing. This introduces a
 layer of indirection that can make debugging hard.

Debugging is best done step by step. You want to be able to sprinkle your code with
`print()` statement to see what your data looks like after every operation, you want
to be able to use `pdb`. You can achieve this by **running your model eagerly**. With
 eager execution, the Python code you write is the code that gets executed.

Simply pass `run_eagerly=True` to `compile()`:

```python
model.compile(optimizer='adam', loss='mse', run_eagerly=True)
```

Of course, the downside is that it makes your model significantly slower. Make sure to
switch it back off to get the benefits of compiled computation graphs once you are
 done debugging!

In general, you will use `run_eagerly=True` every time you need to debug what's
 happening inside your `fit()` call.
"""

"""
## Speeding up training with multiple GPUs

Keras has built-in industry-strength support for multi-GPU training and distributed
 multi-worker training, via the `tf.distribute` API.

If you have multiple GPUs on your machine, you can train your model on all of them by:

- Creating a `tf.distribute.MirroredStrategy` object
- Building & compiling your model inside the strategy's scope
- Calling `fit()` and `evaluate()` on a dataset as usual

```python
# Create a MirroredStrategy.
strategy = tf.distribute.MirroredStrategy()

# Open a strategy scope.
with strategy.scope():
  # Everything that creates variables should be under the strategy scope.
  # In general this is only model construction & `compile()`.
  model = Model(...)
  model.compile(...)

# Train the model on all available devices.
train_dataset, val_dataset, test_dataset = get_dataset()
model.fit(train_dataset, epochs=2, validation_data=val_dataset)

# Test the model on all available devices.
model.evaluate(test_dataset)
```

For a detailed introduction to multi-GPU & distributed training, see
[this guide](/guides/distributed_training/).
"""

"""
## Doing preprocessing synchronously on-device vs. asynchronously on host CPU

You've learned about preprocessing, and you've seen example where we put image
 preprocessing layers (`CenterCrop` and `Rescaling`) directly inside our model.

Having preprocessing happen as part of the model during training
is great if you want to do on-device preprocessing, for instance, GPU-accelerated
feature normalization or image augmentation. But there are kinds of preprocessing that
are not suited to this setup: in particular, text preprocessing with the
`TextVectorization` layer. Due to its sequential nature and due to the fact that it
 can only run on CPU, it's often a good idea to do **asynchronous preprocessing**.

With asynchronous preprocessing, your preprocessing operations will run on CPU, and the
preprocessed samples will be buffered into a queue while your GPU is busy with
previous batch of data. The next batch of preprocessed samples will then be fetched
from the queue to the GPU memory right before the GPU becomes available again
(prefetching). This ensures that preprocessing will not be blocking and that your GPU
 can run at full utilization.

To do asynchronous preprocessing, simply use `dataset.map` to inject a preprocessing
 operation into your data pipeline:
"""

# Example training data, of dtype `string`.
samples = np.array([["This is the 1st sample."], ["And here's the 2nd sample."]])
labels = [[0], [1]]

# Prepare a TextVectorization layer.
vectorizer = TextVectorization(output_mode="int")
vectorizer.adapt(samples)

# Asynchronous preprocessing: the text vectorization is part of the tf.data pipeline.
# First, create a dataset
dataset = tf.data.Dataset.from_tensor_slices((samples, labels)).batch(2)
# Apply text vectorization to the samples
dataset = dataset.map(lambda x, y: (vectorizer(x), y))
# Prefetch with a buffer size of 2 batches
dataset = dataset.prefetch(2)

# Our model should expect sequences of integers as inputs
inputs = keras.Input(shape=(None,), dtype="int64")
x = layers.Embedding(input_dim=10, output_dim=32)(inputs)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="mse", run_eagerly=True)
model.fit(dataset)

"""
Compare this to doing text vectorization as part of the model:
"""

# Our dataset will yield samples that are strings
dataset = tf.data.Dataset.from_tensor_slices((samples, labels)).batch(2)

# Our model should expect strings as inputs
inputs = keras.Input(shape=(1,), dtype="string")
x = vectorizer(inputs)
x = layers.Embedding(input_dim=10, output_dim=32)(x)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer="adam", loss="mse", run_eagerly=True)
model.fit(dataset)

"""
When training text models on CPU, you will generally not see any performance difference
between the two setups. When training on GPU, however, doing asynchronous buffered
preprocessing on the host CPU while the GPU is running the model itself can result in
 a significant speedup.

After training, if you to export an end-to-end model that includes the preprocessing
 layer(s), this is easy to do, since `TextVectorization` is a layer:

```python
inputs = keras.Input(shape=(1,), dtype='string')
x = vectorizer(inputs)
outputs = trained_model(x)
end_to_end_model = keras.Model(inputs, outputs)
```
"""

"""
## Finding the best model configuration with hyperparameter tuning

Once you have a working model, you're going to want to optimize its configuration --
architecture choices, layer sizes, etc. Human intuition can only go so far, so you'll
 want to leverage a systematic approach: hyperparameter search.

You can use
[Keras Tuner](https://keras-team.github.io/keras-tuner/documentation/tuners/) to find
 the best hyperparameter for your Keras models. It's as easy as calling `fit()`.

Here how it works.

First, place your model definition in a function, that takes a single `hp` argument.
Inside this function, replace any value you want to tune with a call to hyperparameter
 sampling methods, e.g. `hp.Int()` or `hp.Choice()`:

```python
def build_model(hp):
    inputs = keras.Input(shape=(784,))
    x = layers.Dense(
        units=hp.Int('units', min_value=32, max_value=512, step=32),
        activation='relu'))(inputs)
    outputs = layers.Dense(10, activation='softmax')(x)
    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(
            hp.Choice('learning_rate',
                      values=[1e-2, 1e-3, 1e-4])),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'])
    return model
```

The function should return a compiled model.

Next, instantiate a tuner object specifying your optimiation objective and other search
 parameters:


```python
import kerastuner

tuner = kerastuner.tuners.Hyperband(
  build_model,
  objective='val_loss',
  max_epochs=100,
  max_trials=200,
  executions_per_trial=2,
  directory='my_dir')
```

Finally, start the search with the `search()` method, which takes the same arguments as
 `Model.fit()`:

```python
tuner.search(dataset, validation_data=val_dataset)
```

When search is over, you can retrieve the best model(s):

```python
models = tuner.get_best_models(num_models=2)
```

Or print a summary of the results:

```python
tuner.results_summary()
```

"""

"""
## End-to-end examples

To familiarize yourself with the concepts in this introduction, see the following
 end-to-end examples:

- [Text classification](/examples/nlp/text_classification_from_scratch/)
- [Image classification](/examples/vision/image_classification_from_scratch/)
- [Credit card fraud detection](/examples/structured_data/imbalanced_classification/)

"""

"""
## What to learn next

- Learn more about the
[Functional API](/guides/functional_api/).
- Learn more about the
[features of `fit()` and `evaluate()`](/guides/training_with_built_in_methods/).
- Learn more about
[callbacks](/guides/writing_your_own_callbacks/).
- Learn more about
[creating your own custom training steps](/guides/customizing_what_happens_in_fit/).
- Learn more about
[multi-GPU and distributed training](/guides/distributed_training/).
- Learn how to do [transfer learning](/guides/transfer_learning/).
"""
