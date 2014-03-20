def predict_species(sepal_width, petal_length, petal_width):
    """ Predictor for species from model/52952081035d07727e01d836
        Predictive model by BigML - Machine Learning Made Easy
    """
    # 0 == Iris-virginica
    # 1 == Iris-versicolor
    # 2 == Iris-setosa
    if (petal_width > 0.8):
        if (petal_width <= 1.75):
            if (petal_length > 4.95):
                if (petal_width <= 1.55):
                    return 0
                if (petal_width > 1.55):
                    if (petal_length > 5.45):
                        return 0
                    if (petal_length <= 5.45):
                        return 1
            if (petal_length <= 4.95):
                if (petal_width <= 1.65):
                    return 1
                if (petal_width > 1.65):
                    return 0
        if (petal_width > 1.75):
            if (petal_length > 4.85):
                return 0
            if (petal_length <= 4.85):
                if (sepal_width <= 3.1):
                    return 0
                if (sepal_width > 3.1):
                    return 1
    if (petal_width <= 0.8):
        return 2



# ====================================================================



def predict_species_orig(sepal_width=None,
                         petal_length=None,
                         petal_width=None):
    """ Predictor for species from model/52952081035d07727e01d836

        Predictive model by BigML - Machine Learning Made Easy
    """
    if (petal_width is None):
        return u'Iris-virginica'
    if (petal_width > 0.8):
        if (petal_width <= 1.75):
            if (petal_length is None):
                return u'Iris-versicolor'
            if (petal_length > 4.95):
                if (petal_width <= 1.55):
                    return u'Iris-virginica'
                if (petal_width > 1.55):
                    if (petal_length > 5.45):
                        return u'Iris-virginica'
                    if (petal_length <= 5.45):
                        return u'Iris-versicolor'
            if (petal_length <= 4.95):
                if (petal_width <= 1.65):
                    return u'Iris-versicolor'
                if (petal_width > 1.65):
                    return u'Iris-virginica'
        if (petal_width > 1.75):
            if (petal_length is None):
                return u'Iris-virginica'
            if (petal_length > 4.85):
                return u'Iris-virginica'
            if (petal_length <= 4.85):
                if (sepal_width is None):
                    return u'Iris-virginica'
                if (sepal_width <= 3.1):
                    return u'Iris-virginica'
                if (sepal_width > 3.1):
                    return u'Iris-versicolor'
    if (petal_width <= 0.8):
        return u'Iris-setosa'