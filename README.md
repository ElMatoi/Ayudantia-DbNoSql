# AYUDANTIA-DB-No-Sql
Este repo es un ejemplo de uso de redis y mongo usando fastapi para que se guien en su ultimo taller

## Instrucciones
### Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```
### Construir y evantar los Servicios del backend y la base de datos

```bash
docker-compose up --build
```
## API 

### Información de la solicitud basicas 
#### Obtener datos de la cache
- **URL**: `/getSensor/sensor-123-fdc7a306-6bfc-4f69-aa8e-bd8e3046aae1`
- **Método**: `Get`
##### Insertar datos en la cache
- **URL**: `/saveDataSensorInCache`
- **Método**: `Post`
- **Cuerpo** :
  ```bash
  {
  "sensorId": "sensor-123",
  "value": 25.6,
  "unit": "C",
  "timestamp": "2025-04-11T10:30:00"}```
##### volcar datos de redis a mongo
- **URL**: `/volcarDatosRedisAMongo/`
- **Método**: `Post`

