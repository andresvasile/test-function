# 📚 Books MCP Server - Azure Functions

Esta es la versión de Azure Functions del MCP server de books, adaptada para funcionar como una función HTTP en Azure.

## 🚀 Características

- **API REST completa**: Todos los métodos del MCP server disponibles vía HTTP
- **Compatibilidad con Azure Functions**: Optimizado para el entorno serverless
- **Manejo de errores robusto**: Respuestas HTTP apropiadas y manejo de excepciones
- **Datos en memoria**: Misma funcionalidad que el MCP server original

## 📁 Estructura de Archivos

```
azure_function/
├── __init__.py          # Función principal de Azure Functions
├── function.json        # Configuración del trigger HTTP
├── host.json           # Configuración del host de Azure Functions
├── requirements.txt    # Dependencias de Python
├── local.settings.json # Configuración local (no subir a Git)
└── README.md          # Este archivo
```

## 🛠️ Métodos Disponibles

### GET/POST `/api/books`

Todos los métodos se acceden a través del mismo endpoint usando el parámetro `method`:

#### 1. **list_books** - Listar libros
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=list_books&genre=Fantasía&available_only=true"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "list_books", "genre": "Fantasía", "available_only": true}'
```

#### 2. **search_books** - Buscar libros
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=search_books&query=Tolkien"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "search_books", "query": "Tolkien"}'
```

#### 3. **get_book_details** - Detalles de un libro
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=get_book_details&book_id=1"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "get_book_details", "book_id": 1}'
```

#### 4. **add_book** - Agregar libro
```bash
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "add_book",
    "title": "El Hobbit",
    "author": "J.R.R. Tolkien",
    "genre": "Fantasía",
    "year": 1937,
    "pages": 310,
    "description": "Las aventuras de Bilbo Bolsón en la Tierra Media."
  }'
```

#### 5. **borrow_book** - Prestar libro
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=borrow_book&book_id=1"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "borrow_book", "book_id": 1}'
```

#### 6. **return_book** - Devolver libro
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=return_book&book_id=1"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "return_book", "book_id": 1}'
```

#### 7. **rate_book** - Calificar libro
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=rate_book&book_id=1&rating=4.9"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "rate_book", "book_id": 1, "rating": 4.9}'
```

#### 8. **get_library_stats** - Estadísticas
```bash
# GET
curl "https://your-function-app.azurewebsites.net/api/books?method=get_library_stats"

# POST
curl -X POST "https://your-function-app.azurewebsites.net/api/books" \
  -H "Content-Type: application/json" \
  -d '{"method": "get_library_stats"}'
```

## 📊 Formato de Respuesta

Todas las respuestas siguen este formato:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "count": 5
}
```

En caso de error:

```json
{
  "error": "Error description",
  "details": "Additional error details"
}
```

## 🚀 Despliegue en Azure

### Prerrequisitos

1. **Azure CLI** instalado
2. **Azure Functions Core Tools** instalado
3. **Python 3.9+** instalado
4. Cuenta de Azure con permisos para crear recursos

### Pasos de Despliegue

#### 1. Instalar Azure Functions Core Tools
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

#### 2. Iniciar sesión en Azure
```bash
az login
```

#### 3. Crear un grupo de recursos
```bash
az group create --name books-mcp-rg --location "East US"
```

#### 4. Crear una cuenta de almacenamiento
```bash
az storage account create \
  --name booksmcpstorage \
  --location "East US" \
  --resource-group books-mcp-rg \
  --sku Standard_LRS
```

#### 5. Crear la Function App
```bash
az functionapp create \
  --resource-group books-mcp-rg \
  --consumption-plan-location "East US" \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name books-mcp-function \
  --storage-account booksmcpstorage
```

#### 6. Desplegar el código
```bash
# Desde el directorio azure_function
func azure functionapp publish books-mcp-function
```

#### 7. Configurar la Function Key (opcional)
```bash
# Obtener la URL y key de la función
az functionapp function keys list \
  --name books-mcp-function \
  --resource-group books-mcp-rg \
  --function-name books
```

### 🔧 Configuración Local

Para probar localmente:

1. **Instalar dependencias**:
```bash
cd azure_function
pip install -r requirements.txt
```

2. **Ejecutar localmente**:
```bash
func start
```

3. **Probar la función**:
```bash
curl "http://localhost:7071/api/books?method=get_library_stats"
```

## 🔐 Autenticación

La función está configurada con `authLevel: "function"`, lo que significa que requiere una Function Key. Puedes:

1. **Obtener la key**:
```bash
az functionapp function keys list \
  --name books-mcp-function \
  --resource-group books-mcp-rg \
  --function-name books
```

2. **Usar la key en las requests**:
```bash
curl "https://books-mcp-function.azurewebsites.net/api/books?method=get_library_stats&code=YOUR_FUNCTION_KEY"
```

## 📝 Notas Importantes

- **Datos en memoria**: Los datos se pierden cuando la función se reinicia
- **Cold start**: La primera llamada puede ser más lenta
- **Timeout**: Configurado para 5 minutos máximo
- **Escalabilidad**: Azure Functions escala automáticamente según la demanda

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Asegúrate de que las dependencias estén en requirements.txt
pip freeze > requirements.txt
```

### Error: "Function not found"
```bash
# Verifica que el archivo function.json esté en la ubicación correcta
# y que el nombre de la función coincida
```

### Error: "Authentication failed"
```bash
# Verifica que estés usando la Function Key correcta
# o cambia authLevel a "anonymous" en function.json para desarrollo
```

## 🔄 Migración desde MCP Server

Para migrar desde el MCP server original:

1. **Cambiar el endpoint**: De `stdio` a HTTP
2. **Cambiar el formato de parámetros**: De argumentos de función a JSON/query params
3. **Manejar respuestas HTTP**: Las respuestas ahora son JSON con códigos de estado
4. **Autenticación**: Agregar Function Key a las requests

## 📚 Ejemplos de Uso

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function listBooks() {
  try {
    const response = await axios.get(
      'https://books-mcp-function.azurewebsites.net/api/books',
      {
        params: {
          method: 'list_books',
          available_only: true
        },
        headers: {
          'x-functions-key': 'YOUR_FUNCTION_KEY'
        }
      }
    );
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}
```

### Python
```python
import requests

def list_books():
    url = 'https://books-mcp-function.azurewebsites.net/api/books'
    params = {
        'method': 'list_books',
        'available_only': True
    }
    headers = {
        'x-functions-key': 'YOUR_FUNCTION_KEY'
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# Uso
books = list_books()
print(books)
```

### cURL
```bash
# Listar libros disponibles
curl "https://books-mcp-function.azurewebsites.net/api/books?method=list_books&available_only=true&code=YOUR_FUNCTION_KEY"

# Agregar un nuevo libro
curl -X POST "https://books-mcp-function.azurewebsites.net/api/books?code=YOUR_FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "add_book",
    "title": "El Hobbit",
    "author": "J.R.R. Tolkien",
    "genre": "Fantasía",
    "year": 1937,
    "pages": 310,
    "description": "Las aventuras de Bilbo Bolsón en la Tierra Media."
  }'
```
#   t e s t - f u n c t i o n  
 