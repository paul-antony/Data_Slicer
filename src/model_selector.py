from sklearn.linear_model import LogisticRegression

model_list = {1: LogisticRegression
              }


def model_select(i):
    return model_list[i]()