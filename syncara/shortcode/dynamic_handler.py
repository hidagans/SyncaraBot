import importlib.util
import os
from syncara import console

DYNAMIC_DIR = os.path.join(os.path.dirname(__file__), "dynamic")
PENDING_DIR = os.path.join(os.path.dirname(__file__), "pending")
os.makedirs(DYNAMIC_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)

# Template AI untuk generate kode handler dari deskripsi
AI_HANDLER_TEMPLATE = '''
async def {func_name}(client, message, params):
    """{description}"""
    try:
        # IMPLEMENTASI OTOMATIS DARI DESKRIPSI
        {body}
    except Exception as e:
        await message.reply(f'Error: {{e}}')
    return True
'''

def generate_handler_code(shortcode_name, description=None):
    # Contoh AI: jika ada kata "kali", generate handler perkalian
    func_name = shortcode_name.lower().replace(':', '_')
    if description and 'kali' in description.lower():
        body = "a, b = map(int, params.split(','))\n        await message.reply(str(a * b))"
    else:
        body = "await message.reply(params[::-1])"
    return AI_HANDLER_TEMPLATE.format(func_name=func_name, description=description or '', body=body)

# Handler baru masuk pending approval
async def request_handler_approval(shortcode_name, description, message):
    filename = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    code = generate_handler_code(shortcode_name, description)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    await message.reply(f"Handler `{shortcode_name}` siap di-approve.\n\nKode:\n```python\n{code}\n```\n\nBalas dengan /approve {shortcode_name} untuk mengaktifkan, atau /reject {shortcode_name} untuk membatalkan.")
    console.info(f"[DYNAMIC] Handler {shortcode_name} pending approval at {filename}")
    return filename

def approve_handler(shortcode_name, registry=None):
    pending_file = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    if not os.path.exists(pending_file):
        return False, "Handler tidak ditemukan di pending."
    dynamic_file = os.path.join(DYNAMIC_DIR, f"{shortcode_name.lower()}.py")
    os.rename(pending_file, dynamic_file)
    # Import handler
    spec = importlib.util.spec_from_file_location(shortcode_name, dynamic_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler_func = getattr(module, shortcode_name.lower().replace(':', '_'))
    if registry is not None:
        registry[shortcode_name] = handler_func
    console.info(f"[DYNAMIC] Handler {shortcode_name} approved and registered from {dynamic_file}")
    return True, "Handler sudah aktif!"

def reject_handler(shortcode_name):
    pending_file = os.path.join(PENDING_DIR, f"{shortcode_name.lower()}.py")
    if os.path.exists(pending_file):
        os.remove(pending_file)
        return True, "Handler dibatalkan."
    return False, "Handler tidak ditemukan di pending."

def create_and_register_handler(shortcode_name, description=None, registry=None):
    filename = os.path.join(DYNAMIC_DIR, f"{shortcode_name.lower()}.py")
    code = generate_handler_code(shortcode_name, description)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    # Import handler
    spec = importlib.util.spec_from_file_location(shortcode_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler_func = getattr(module, shortcode_name.lower())
    if registry is not None:
        registry[shortcode_name] = handler_func
    console.info(f"[DYNAMIC] Handler {shortcode_name} registered from {filename}")
    return handler_func 