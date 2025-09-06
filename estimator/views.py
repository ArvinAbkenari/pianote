from django.shortcuts import render
from users.forms import UserSignupForm
import joblib
import pandas as pd
import numpy as np
import os
from django.conf import settings
import ast
from users.views import session_login_required


pipeline = joblib.load(os.path.join(settings.BASE_DIR, "model_pipeline.pkl"))

model = pipeline["model"]
ordinal_encoder = pipeline["ordinal_encoder"]
color_binarizer = pipeline["color_binarizer"]
finish_binarizer = pipeline["finish_binarizer"]

# Create your views here.
@session_login_required
def estimator_view(request):
    dollar_price = 95000
    signup_form = UserSignupForm()
    prediction = None
    df = pd.read_csv("data.csv")
    def safe_parse(val):
        try:
            return ast.literal_eval(val)
        except Exception:
            return []

    df["color_array"] = df["color_array"].apply(safe_parse)
    df["finish"] = df["finish"].apply(safe_parse)

    all_colors = set()
    df["color_array"].apply(all_colors.update)

    all_finishes = set()
    df["finish"].apply(all_finishes.update)

    brands = sorted(df["brand"].dropna().unique())
    models = sorted(df["model"].dropna().unique())
    types = sorted(df["type"].dropna().unique())
    unique_colors = sorted(all_colors)
    unique_finishes = sorted(all_finishes)

    if request.method == "POST":
        brand = request.POST.get("brand")
        model_name = request.POST.get("model")
        material = request.POST.get("material")
        finish = request.POST.get("finish")
        types = request.POST.get("types")
        type_grand = ""
        type_vertical = ""
        if types == 'vertical':
            type_grand = False
            type_vertical = True
        elif types == 'grand':
            type_grand = True
            type_vertical = False
        dimension = request.POST.get("dimension")
        input_df = pd.DataFrame([{
            "brand": brand,
            "model": model_name,
            "color_array": [material],  
            "finish": [finish],         
            "dimension": float(dimension),
            "type_grand" : type_grand,
            "type_vertical" : type_vertical
        }])
        processed = preprocess_input(input_df)
        prediction = int(model.predict(processed)[0]* dollar_price)
    return render(request, "estimator/estimator.html", {
        "form": signup_form,
        "brands": brands,
        "models": models,
        "types": types,
        "all_colors": unique_colors,
        "all_finish": unique_finishes,
        "prediction": prediction
    })

def preprocess_input(df):
    def safe_parse(val):
        try:
            return ast.literal_eval(val)
        except Exception:
            return []
    df = df.copy()
    for i, col in enumerate(["brand", "model"]):
        known_classes = list(ordinal_encoder.categories_[i])
        df[col] = df[col].apply(lambda x: x if x in known_classes else "<unknown>")

    df[["brand", "model"]] = ordinal_encoder.transform(df[["brand", "model"]])

    df["color_array"] = df["color_array"].apply(safe_parse)
    df["finish"] = df["finish"].apply(safe_parse)
    color_encoded = pd.DataFrame(
        color_binarizer.transform(df["color_array"]),
        columns=[f"color_{c}" for c in color_binarizer.classes_],
        index=df.index
    )

    finish_encoded = pd.DataFrame(
        finish_binarizer.transform(df["finish"]),
        columns=[f"finish_{f}" for f in finish_binarizer.classes_],
        index=df.index
    )

    df = pd.concat([df.drop(["color_array", "finish"], axis=1), color_encoded, finish_encoded], axis=1)
    return df
