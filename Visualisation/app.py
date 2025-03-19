from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer

app = FastAPI()

# ✅ Load Hugging Face models dynamically from the internet
code_generator = pipeline("text-generation", model="bigcode/starcoder",times_out=1000)
user_input_processor = pipeline("text-generation", model="tiiuae/falcon-7b-instruct")  # comprend lsngusge naturel
table_analyzer = pipeline("table-question-answering", model="google/tapas-large")
#image_captioner = pipeline("image-to-text", model="Salesforce/blip2-opt-2.7b")

# ✅ Load T5 Model (ensure correct architecture)
model_name = "google/t5-small"  # Change to the correct T5 model if needed
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

@app.post("/visualize/")
async def visualize(
    file: UploadFile = File(...),
    description: str = Form(None),
    chart_type: str = Form(None),
    x_column: str = Form(None),
    y_column: str = Form(None)
):
    print("🔵 Début du traitement...")

    contents = await file.read()
    excel_data = io.BytesIO(contents)
    print("✅ Fichier reçu et converti en mémoire.")

    try:
        df = pd.read_excel(excel_data)
        print("✅ Lecture du fichier Excel réussie.")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier Excel : {e}")
        return {"error": "Impossible de lire le fichier Excel."}

    df.columns = df.columns.str.strip().str.lower()
    print("📌 Colonnes après nettoyage :", df.columns.tolist())

    # If no specific chart details are given, infer from description
    if description:
        print("📝 Analyse de la description utilisateur...")
        response = user_input_processor(description, max_length=50)
        inferred_data = response[0]['generated_text']
        print("🔍 Inference AI:", inferred_data)
        # TODO: Extract structured data from response (chart_type, x_column, y_column)

    # Ensure x_column and y_column exist
    if x_column.lower() not in df.columns or y_column.lower() not in df.columns:
        print(f"❌ Erreur: '{x_column}' ou '{y_column}' non trouvées.")
        return {"error": f"Les colonnes '{x_column}' ou '{y_column}' n'existent pas."}

    print("✅ Colonnes valides, préparation du graphique...")

    plt.figure(figsize=(20, 12))
    if chart_type == "bar":
        df.plot(kind="bar", x=x_column.lower(), y=y_column.lower())
    elif chart_type == "line":
        df.plot(kind="line", x=x_column.lower(), y=y_column.lower())
    elif chart_type == "scatter":
        df.plot(kind="scatter", x=x_column.lower(), y=y_column.lower())
    elif chart_type == "pie":
        df.set_index(x_column.lower())[y_column.lower()].plot(kind="pie", autopct="%1.1f%%")
    elif chart_type == "histogram":
        df[y_column.lower()].plot(kind="hist", bins=10)
    else:
        return {"error": "Invalid chart type"}

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format="png")
    img_stream.seek(0)
    plt.close()

    # Generate image caption
    #image_description = image_captioner(img_stream)
    #print("🖼️ Description du graphique:", image_description)

    return StreamingResponse(img_stream, media_type="image/png")
