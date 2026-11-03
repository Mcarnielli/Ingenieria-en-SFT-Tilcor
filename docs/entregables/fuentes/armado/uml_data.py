# -*- coding: utf-8 -*-
"""Diagramas UML por caso de uso (vista estática = clases, vista dinámica = secuencia).
Clases y métodos tomados del diseño de la Tesis (cap. 7 DDL, 9.2 modelos, 10.3 gateway, 11 facturación, 13 JWT)."""

CLASES = {
 'Galpon': ['+numero int', '+capacidad_max int'],
 'Raza': ['+nombre string'],
 'TablaGenetica': ['+semana_edad int', '+prod_tabla decimal', '+viab_tabla decimal'],
 'Lote': ['+nro_lote string', '+fecha_inicio date', '+aves_iniciales int', '+activo bool', '+existencia_actual() int', '+semana_edad_actual() int', '+viabilidad_acumulada() decimal'],
 'RegistroProduccion': ['+fecha date', '+semana_edad int', '+huevos_totales int', '+cajones int', '+maples int', '+aves_muertas int', '+existencia int', '+porc_postura() decimal', '+desvio_vs_tabla() decimal', '+tiene_alerta_produccion() bool'],
 'RegistroProduccionViewSet': ['+perform_create()', '+resumen_semanal()', '+curva_vs_tabla()'],
 'AlertaProductiva': ['+nivel string', '+mensaje string', '+fecha date'],
 'Sensor': ['+codigo string', '+tipo tipo_sensor', '+ubicacion string', '+umbral_min decimal', '+umbral_max decimal', '+activo bool'],
 'RegistroSensor': ['+timestamp datetime', '+valor decimal', '+unidad string'],
 'GatewayMQTT': ['+conectar(host, port)', '-_on_message(msg)'],
 'BrokerMosquitto': ['<<externo>>'],
 'MotorAlertas': ['+evaluar(registro)', '-_umbrales(sensor)', '-_nivel(valor, umbrales)'],
 'AlertaIoT': ['+timestamp datetime', '+nivel string', '+valor decimal', '+mensaje string', '+revisada bool'],
 'Notificador': ['+enviar_push()', '+enviar_whatsapp()', '+enviar_email()'],
 'ConsumidorWebSocket': ['+connect()', '+enviar_lectura()'],
 'Usuario': ['+username string', '+password_hash string', '+nombre_completo string', '+rol string', '+activo bool', '+ultimo_acceso datetime'],
 'CustomTokenSerializer': ['+get_token(user)'],
 'AutorizacionPorRol': ['+requiere_rol(roles)'],
 'TareasProgramadas': ['<<Celery>>', '+reporte_diario()', '+informe_semanal()'],
 'GeneradorPDF': ['+generar(indicadores)'],
 'ServicioEmail': ['+enviar(destino, adjunto)'],
 'DashboardPrincipal': ['+kpis()', '+alertas_activas()', '+resumen_comercial()'],
 'PlanImplementacion': ['+fases list', '+guardar(progreso)', '+descartar()'],
 'FasePlan': ['+nombre string', '+porcentaje int'],
 'Cliente': ['+razon_social string', '+cuit string', '+condicion_iva string', '+categoria string', '+limite_credito decimal'],
 'Pedido': ['+fecha datetime', '+estado string', '+total decimal'],
 'CuentaCorriente': ['+tipo_movimiento string', '+importe decimal', '+saldo_parcial decimal'],
 'Factura': ['+nro_factura string', '+tipo_comprobante char', '+cae string', '+cae_vto date', '+total_factura decimal'],
 'ServicioFacturacion': ['+emitir_factura(pedido)', '-_preparar_datos(pedido)', '-_solicitar_cae(datos, nro)'],
 'DonGestion': ['<<sistema externo>>'],
 'ModuloVentas': ['+cargar_iframe()', '+abrir_en_pestana()'],
 'ARCA_AFIP': ['<<WSFE · SOAP>>', '+solicitar_CAE(comprobante)'],
}

def clase(n):
    return 'class %s {\n%s\n}' % (n, '\n'.join('  ' + x for x in CLASES[n]))

# CU -> (clases, relaciones)
EST = {
 'CU01': (['Galpon', 'Raza', 'TablaGenetica', 'Lote', 'RegistroProduccion', 'RegistroProduccionViewSet'],
          ['Galpon "1" --> "*" Lote', 'Raza "1" --> "*" Lote', 'Raza "1" --> "*" TablaGenetica', 'Lote "1" --> "*" RegistroProduccion', 'RegistroProduccionViewSet ..> RegistroProduccion : crea', 'RegistroProduccion ..> TablaGenetica : compara con']),
 'CU02': (['Lote', 'RegistroProduccion', 'AlertaProductiva'],
          ['Lote "1" --> "*" RegistroProduccion', 'RegistroProduccion ..> AlertaProductiva : genera si mortalidad supera umbral', 'RegistroProduccion ..> Lote : actualiza existencia']),
 'CU04': (['Lote', 'RegistroProduccion', 'RegistroProduccionViewSet', 'TablaGenetica'],
          ['Lote "1" --> "*" RegistroProduccion', 'RegistroProduccionViewSet ..> RegistroProduccion : lista ultimos registros', 'RegistroProduccion ..> TablaGenetica : desvio en pp']),
 'CU09': (['RegistroProduccionViewSet', 'RegistroProduccion', 'TablaGenetica', 'Lote'],
          ['RegistroProduccionViewSet ..> RegistroProduccion : serie real', 'RegistroProduccionViewSet ..> TablaGenetica : serie de tabla', 'Lote "1" --> "*" RegistroProduccion']),
 'CU03': (['Sensor', 'RegistroSensor', 'Galpon', 'ConsumidorWebSocket'],
          ['Galpon "1" --> "*" Sensor', 'Sensor "1" --> "*" RegistroSensor', 'ConsumidorWebSocket ..> RegistroSensor : ultimo valor por sensor']),
 'CU05': (['Usuario', 'Sensor', 'MotorAlertas'],
          ['Usuario ..> Sensor : configura umbral_min y umbral_max', 'MotorAlertas ..> Sensor : lee umbrales vigentes']),
 'CU06': (['MotorAlertas', 'Sensor', 'RegistroSensor', 'AlertaIoT', 'Notificador'],
          ['Sensor "1" --> "*" RegistroSensor', 'MotorAlertas ..> RegistroSensor : evalua', 'MotorAlertas ..> AlertaIoT : registra Warning', 'AlertaIoT ..> Notificador : push al supervisor']),
 'CU07': (['MotorAlertas', 'RegistroSensor', 'AlertaIoT', 'Notificador'],
          ['MotorAlertas ..> RegistroSensor : evalua', 'MotorAlertas ..> AlertaIoT : registra Critico', 'AlertaIoT ..> Notificador : push y WhatsApp']),
 'CU08': (['ConsumidorWebSocket', 'Sensor', 'RegistroSensor', 'AlertaIoT'],
          ['Sensor "1" --> "*" RegistroSensor', 'ConsumidorWebSocket ..> RegistroSensor : emite lecturas nuevas', 'ConsumidorWebSocket ..> AlertaIoT : log de alertas del dia']),
 'CU19-22': (['Sensor', 'BrokerMosquitto', 'GatewayMQTT', 'RegistroSensor', 'MotorAlertas', 'AlertaIoT', 'Notificador', 'ConsumidorWebSocket'],
          ['Sensor ..> BrokerMosquitto : publica JSON QoS 1', 'BrokerMosquitto ..> GatewayMQTT : entrega mensaje', 'GatewayMQTT ..> RegistroSensor : persiste', 'GatewayMQTT ..> MotorAlertas : evalua', 'MotorAlertas ..> AlertaIoT : registra', 'AlertaIoT ..> Notificador : notifica', 'GatewayMQTT ..> ConsumidorWebSocket : transmite al dashboard']),
 'CU14': (['Lote', 'TablaGenetica', 'Raza'],
          ['Raza "1" --> "*" Lote', 'Raza "1" --> "*" TablaGenetica', 'Lote ..> TablaGenetica : viabilidad vs viab_tabla']),
 'CU16': (['TareasProgramadas', 'Lote', 'RegistroProduccion', 'GeneradorPDF', 'ServicioEmail'],
          ['Lote "1" --> "*" RegistroProduccion', 'TareasProgramadas ..> RegistroProduccion : consolida la semana', 'TareasProgramadas ..> GeneradorPDF : informe', 'TareasProgramadas ..> ServicioEmail : envia al veterinario']),
 'CU17': (['Lote', 'RegistroProduccion', 'AlertaProductiva', 'TablaGenetica'],
          ['Lote "1" --> "*" RegistroProduccion', 'RegistroProduccion ..> AlertaProductiva : umbral de mortalidad', 'Lote ..> TablaGenetica : viabilidad de referencia']),
 'CU18': (['Lote', 'RegistroProduccion', 'AlertaProductiva'],
          ['Lote "1" --> "*" RegistroProduccion', 'RegistroProduccion ..> AlertaProductiva : referencia Warning 0,5 %']),
 'CU10': (['PlanImplementacion', 'FasePlan'],
          ['PlanImplementacion "1" --> "5" FasePlan']),
 'CU12': (['DashboardPrincipal', 'RegistroProduccion', 'Lote', 'RegistroSensor', 'PlanImplementacion', 'DonGestion'],
          ['DashboardPrincipal ..> RegistroProduccion : produccion y postura', 'DashboardPrincipal ..> Lote : viabilidad', 'DashboardPrincipal ..> RegistroSensor : alertas IoT', 'DashboardPrincipal ..> PlanImplementacion : plan', 'DashboardPrincipal ..> DonGestion : resumen comercial']),
 'CU13': (['TareasProgramadas', 'RegistroProduccion', 'GeneradorPDF', 'ServicioEmail', 'Usuario'],
          ['TareasProgramadas ..> RegistroProduccion : lee el dia', 'TareasProgramadas ..> GeneradorPDF : reporte', 'TareasProgramadas ..> ServicioEmail : envia', 'ServicioEmail ..> Usuario : propietario']),
 'CU15': (['Usuario', 'CustomTokenSerializer', 'AutorizacionPorRol'],
          ['CustomTokenSerializer ..> Usuario : claims de nombre, rol y galpones', 'AutorizacionPorRol ..> CustomTokenSerializer : lee el rol del token']),
 'CU11': (['Cliente', 'Pedido', 'CuentaCorriente', 'Usuario', 'Notificador'],
          ['Cliente "1" --> "*" Pedido', 'Cliente "1" --> "*" CuentaCorriente', 'Pedido ..> Notificador : aprobacion pendiente', 'Notificador ..> Usuario : supervisor']),
 'CU23': (['ModuloVentas', 'DonGestion', 'Usuario'],
          ['Usuario ..> ModuloVentas : rol Admin', 'ModuloVentas ..> DonGestion : iframe']),
 'CU24': (['Pedido', 'ServicioFacturacion', 'Factura', 'CuentaCorriente', 'DonGestion', 'ARCA_AFIP'],
          ['Pedido "1" --> "0..1" Factura', 'DonGestion ..> ServicioFacturacion : confirma entrega', 'ServicioFacturacion ..> ARCA_AFIP : solicita CAE', 'ServicioFacturacion ..> Factura : guarda CAE', 'Factura ..> CuentaCorriente : actualiza saldo']),
}

H = 'sequenceDiagram\n  autonumber\n'
DIN = {
'CU01': H + '''  actor Op as Operario de Galpón
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  Op->>App: Abre la sección Producción
  App-->>Op: Formulario con fecha, semana, huevos, cajones, maples, muertas y existencia
  Op->>App: Completa huevos y existencia
  App-->>Op: Calcula el % de postura en tiempo real
  Op->>App: Guardar registro
  alt existencia igual a 0
    App-->>Op: Error de validación, no guarda
  else datos válidos
    App->>API: POST registro de producción
    API->>BD: Consulta tabla genética (raza, semana)
    BD-->>API: prod_tabla
    API->>API: desvio_vs_tabla()
    alt desvío menor a -5 pp
      API-->>App: Indicador de alerta
      App-->>Op: Modal de alerta, ofrece notificar al supervisor
    end
    API->>BD: Guarda el registro
    API-->>App: 201 Creado
    App-->>Op: Historial de 7 días actualizado
  end''',
'CU02': H + '''  actor Op as Operario de Galpón
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  actor Sup as Supervisor
  Op->>App: Ingresa las aves muertas del día
  alt muertas mayor a la existencia
    App-->>Op: Error de validación
  else valor válido
    App->>API: POST registro con aves_muertas
    API->>BD: Actualiza existencia del lote
    API->>API: Calcula mortalidad semanal acumulada
    alt mortalidad mayor a 1,0 %
      API-->>Sup: Alerta Crítico (CU07)
    else mortalidad mayor a 0,5 %
      API-->>Sup: Alerta Warning (CU06)
    end
    API-->>App: Registro guardado
    App-->>Op: Confirmación
  end''',
'CU04': H + '''  actor U as Operario o Supervisor
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Abre la sección Producción
  App->>API: GET últimos 7 registros
  API->>BD: Consulta registros y tabla genética
  BD-->>API: Registros con prod_tabla
  API-->>App: Registros con % postura y desvío en pp
  alt hay registros
    App-->>U: Historial (verde, naranja o rojo según desvío)
  else no hay registros
    App-->>U: Mensaje Sin registros disponibles
  end
  opt rol Supervisor
    App-->>U: Gráfica de postura real vs tabla genética
  end''',
'CU09': H + '''  actor U as Supervisor o Propietario
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Abre el dashboard o Producción
  App->>API: GET curva_vs_tabla del lote activo
  API->>BD: Registros de producción del lote
  BD-->>API: Postura real por semana
  API->>BD: Valores de tabla genética de la raza
  BD-->>API: Postura de tabla por semana
  API-->>App: Dos series y desvío acumulado
  App-->>U: Gráfica (real sólida, tabla punteada) y badge de desvío''',
'CU03': H + '''  actor U as Operario o Supervisor
  participant App as App TILCOR (PWA)
  participant WS as WebSocket (Channels)
  participant BD as TimescaleDB
  U->>App: Abre la sección IoT
  App->>WS: Abre la conexión
  WS->>BD: Último valor de cada sensor
  BD-->>WS: Lecturas con timestamp
  WS-->>App: Valores y estado por sensor
  App-->>U: Panel con semáforo verde, amarillo o rojo
  loop cada lectura nueva
    WS-->>App: Valor actualizado
    App-->>U: Refresca la tarjeta del sensor
  end
  alt sin conexión
    App-->>U: Última versión en caché y hora del último dato
  end''',
'CU05': H + '''  actor Sup as Supervisor
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  participant MA as MotorAlertas
  Sup->>App: Abre la configuración de alertas IoT
  App->>API: GET sensores y umbrales
  API-->>App: Lista de sensores con umbral_min y umbral_max
  Sup->>App: Elige un sensor y modifica los umbrales
  alt mínimo mayor o igual al máximo
    App-->>Sup: Error de validación, no guarda
  else valores válidos
    Sup->>App: Confirma
    App->>API: PATCH sensor
    API->>BD: Guarda umbral_min y umbral_max
    API->>MA: Aplica los nuevos umbrales
    API-->>App: Configuración guardada
  end''',
'CU06': H + '''  participant MA as MotorAlertas
  participant BD as PostgreSQL
  participant N as Notificador
  actor Sup as Supervisor
  participant Dash as Dashboard
  MA->>MA: Evalúa el dato contra el umbral del sensor
  MA->>MA: Clasifica como Warning (fuera de rango, sin superar 110 % del umbral)
  MA->>BD: Registra la alerta (timestamp, origen, valor, umbral, nivel)
  MA->>N: Solicita notificación con acción recomendada
  N->>Sup: Push en menos de 2 minutos
  MA->>Dash: Semáforo en amarillo
  Sup->>Dash: Revisa y marca la alerta como resuelta
  opt supervisor sin conexión
    N->>N: Encola la notificación hasta recuperar conectividad
  end''',
'CU07': H + '''  participant MA as MotorAlertas
  participant BD as PostgreSQL
  participant N as Notificador
  actor Sup as Supervisor
  actor Vet as Veterinario externo
  participant Dash as Dashboard
  MA->>MA: Evalúa el dato y detecta nivel Crítico
  MA->>BD: Registra la alerta (nivel Crítico, diferencia porcentual)
  MA->>N: Solicita notificación urgente
  N->>Sup: Push y WhatsApp en menos de 2 minutos
  MA->>Dash: Semáforo en rojo con animación
  opt mortalidad crítica
    N->>Vet: Notificación al veterinario
  end
  Sup->>Dash: Toma acción correctiva y marca como resuelta
  opt sin conectividad
    N->>N: Encola con máxima prioridad
  end''',
'CU08': H + '''  actor U as Supervisor u Operario
  participant App as App TILCOR (PWA)
  participant WS as WebSocket (Channels)
  participant BD as TimescaleDB
  U->>App: Abre la sección IoT
  App->>WS: Establece la conexión
  WS->>BD: Últimos valores de los 6 sensores
  BD-->>WS: Lecturas
  WS-->>App: Valores, gráficas de 6 horas y log de alertas del día
  App-->>U: Panel con semáforo, gráficas y alertas
  loop cada dato nuevo
    WS-->>App: Lectura actualizada
    App-->>U: Actualiza panel
  end
  opt historial
    U->>App: Elige variable y rango de fechas
    App->>BD: Consulta histórica
    BD-->>App: Serie temporal
    App-->>U: Gráfica del rango
  end''',
'CU19-22': H + '''  participant S as Sensor (ESP32)
  participant B as Broker MQTT
  participant G as GatewayMQTT
  participant BD as TimescaleDB
  participant MA as MotorAlertas
  participant WS as Dashboard (WebSocket)
  participant N as Notificador
  actor Sup as Supervisor
  S->>B: CU19 publica JSON {sensor_id, valor, unidad, timestamp} con QoS 1
  B->>G: Entrega el mensaje
  G->>G: CU20 valida el formato del payload
  G->>BD: CU20 persiste la lectura
  G->>MA: CU21 evalúa contra los umbrales
  alt sin desvío
    G->>WS: Transmite el dato y finaliza
  else desvío Warning o Crítico
    MA->>BD: Registra la alerta (CU06 o CU07)
    MA->>N: CU22 solicita notificación
    N->>Sup: Push y WhatsApp en menos de 2 minutos
    G->>WS: Transmite dato y semáforo
  end
  opt payload inválido o sensor sin respuesta
    G->>G: Descarta y registra el error en el log
  end''',
'CU14': H + '''  actor U as Propietario o Supervisor
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Abre el dashboard o Sanidad
  App->>API: GET viabilidad de los lotes activos
  API->>BD: Aves en existencia y aves iniciales por lote
  API->>BD: viab_tabla de la raza
  BD-->>API: Datos
  API->>API: viabilidad = existencia / aves iniciales x 100
  API-->>App: Real, tabla y diferencia en pp por lote
  alt diferencia menor a -15 pp
    App-->>U: Barra roja con alerta
  else diferencia menor a -5 pp
    App-->>U: Barra naranja
  else
    App-->>U: Barra normal
  end''',
'CU16': H + '''  participant C as Celery (lunes 08:00)
  participant BD as PostgreSQL
  participant PDF as GeneradorPDF
  participant M as ServicioEmail
  actor Vet as Veterinario externo
  C->>BD: Consolida la mortalidad de la semana
  BD-->>C: Muertas por día y existencia final
  C->>C: Calcula mortalidad semanal y viabilidad acumulada
  C->>PDF: Genera el informe con resumen, curva y alertas
  PDF-->>C: Archivo PDF
  C->>M: Envía el informe al correo del veterinario
  M->>Vet: Correo con PDF adjunto
  C->>BD: Registra el envío en el log de reportes
  opt sin registros en la semana
    C->>M: Informe Sin registros de mortalidad esta semana
  end''',
'CU17': H + '''  actor U as Veterinario o Supervisor
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Abre la sección Sanidad
  App->>API: GET KPIs y mortalidad semanal
  API->>BD: Registros del lote activo
  BD-->>API: Mortalidad por semana y viabilidad
  API-->>App: KPIs, historial y protocolo de alertas
  App-->>U: KPIs de sanidad
  opt mortalidad sobre el umbral
    App-->>U: Alerta de mortalidad
  end
  App-->>U: Gráfica semanal con tendencia y protocolo (Normal, Advertencia, Crítico)''',
'CU18': H + '''  actor U as Veterinario o Supervisor
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Abre la sección Sanidad
  App->>API: GET mortalidad histórica del lote
  API->>BD: Registros semanales
  BD-->>API: Muertas y existencia por semana
  API->>API: Calcula el % de mortalidad semanal
  API-->>App: Serie de semanas
  App-->>U: Gráfica con picos y línea de referencia en 0,5 %
  alt menos de 3 semanas
    App-->>U: Puntos disponibles y nota de datos insuficientes
  end''',
'CU10': H + '''  actor U as Usuario Admin
  participant App as App TILCOR (PWA)
  participant LS as localStorage
  U->>App: Toca Editar en el plan de implementación
  App-->>U: Modal con un slider por fase (5 fases)
  U->>App: Mueve los sliders
  App-->>U: Porcentaje en tiempo real
  alt guarda
    U->>App: Guardar cambios
    App->>LS: Guarda el progreso de las fases
    App-->>U: Barras actualizadas con animación
  else cierra sin guardar
    U->>App: Cierra el modal
    App-->>U: Mantiene el progreso anterior
  end''',
'CU12': H + '''  actor U as Propietario, Supervisor u Operario
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  participant DG as Don Gestión
  U->>App: Abre la app (el dashboard es la pantalla de inicio)
  App-->>U: Saludo dinámico con hora y fecha
  App->>API: GET KPIs del dashboard
  API->>BD: Producción, postura, aves, mortalidad y alertas
  BD-->>API: Datos
  API->>DG: Ventas, cobrado y a cobrar
  DG-->>API: Resumen comercial
  API-->>App: Indicadores
  App-->>U: 8 KPIs, producción de 7 días, curva real vs tabla y viabilidad
  opt hay alertas activas
    App-->>U: Banner de alerta al tope
  end''',
'CU13': H + '''  participant C as Celery (22:00)
  participant BD as PostgreSQL
  participant PDF as GeneradorPDF
  participant M as ServicioEmail
  actor P as Propietario
  C->>BD: Registros de producción del día
  BD-->>C: Huevos, cajones, muertas, existencia y postura
  C->>C: Calcula desvío, mortalidad acumulada y tendencia
  C->>PDF: Genera el reporte con indicadores, gráficas y alertas
  PDF-->>C: Archivo PDF
  C->>M: Envía al correo del propietario
  M->>P: Correo con reporte adjunto
  C->>BD: Registra el envío en el log de reportes
  opt sin registros del día
    C->>M: Reporte Sin producción registrada, solicita verificar al operario
  end''',
'CU15': H + '''  actor U as Usuario
  participant App as App TILCOR (PWA)
  participant API as API REST
  participant BD as PostgreSQL
  U->>App: Ingresa usuario y contraseña
  App->>API: POST credenciales
  API->>BD: Busca el usuario y verifica el hash
  alt credenciales correctas
    API->>API: Genera tokens JWT con rol y galpones
    API-->>App: Access token (15 min) y refresh token (7 días)
    App-->>U: Dashboard con los módulos del rol y mensaje de bienvenida
    Note over App: Admin ve todos los módulos. Empleado no ve Ventas
  else credenciales incorrectas
    API-->>App: 401
    App-->>U: Mensaje de error y limpia la contraseña
  end''',
'CU11': H + '''  participant S as Sistema
  participant BD as PostgreSQL
  actor Sup as Supervisor
  actor V as Vendedor
  actor P as Propietario
  S->>BD: Total del pedido, saldo de cuenta corriente y límite de crédito
  S->>S: Detecta que el pedido supera el límite
  S->>Sup: Notificación de aprobación pendiente con cliente, monto y saldo
  Sup->>Sup: Evalúa el historial de pagos en Don Gestión
  alt aprueba
    Sup->>S: Aprobar
    S->>BD: Confirma el pedido
  else rechaza
    Sup->>S: Rechazar con motivo
    S->>V: Notifica el rechazo
  else sin respuesta
    S->>Sup: Recordatorio a los 30 minutos
    S->>P: Escala al propietario a las 2 horas
  end''',
'CU23': H + '''  actor U as Usuario Admin
  participant App as App TILCOR (PWA)
  participant DG as Don Gestión
  U->>App: Abre la sección Ventas (solo rol Admin)
  App->>DG: Carga el iframe de la empresa
  App-->>U: Muestra el loader
  alt Don Gestión permite el iframe
    DG-->>App: Módulo con datos reales
    U->>DG: Interactúa (Ventas, Clientes, Cuentas, Productos, Informes)
  else bloquea el iframe
    App-->>U: Error y opción de abrir en nueva pestaña
  end''',
'CU24': H + '''  actor V as Vendedor
  participant DG as Don Gestión
  participant A as ARCA / AFIP (WSFE)
  participant BD as Cuenta corriente
  actor C as Cliente
  V->>DG: Confirma la entrega del pedido
  DG->>DG: Determina el tipo de comprobante (A, B o C) según la condición de IVA
  DG->>A: Solicita CAE por SOAP
  alt AFIP responde
    A-->>DG: CAE y fecha de vencimiento
    DG->>BD: Guarda el CAE y actualiza el saldo del cliente
    DG->>DG: Genera el PDF con el CAE
    DG->>C: Envía la factura por email
  else AFIP no responde o devuelve error
    DG->>DG: Guarda el comprobante como pendiente
    DG->>A: Reintenta a los 5 minutos
  end''',
}

THEME = "%%{init: {'theme':'base','themeVariables':{'primaryColor':'#EAF2F8','primaryBorderColor':'#1A5276','primaryTextColor':'#1C1C1C','lineColor':'#1A5276','secondaryColor':'#FEF9E7','tertiaryColor':'#F2F3F4','fontFamily':'Arial','fontSize':'15px','noteBkgColor':'#FEF9E7','actorBkg':'#EAF2F8','actorBorder':'#1A5276','signalColor':'#1A5276'}}}%%\n"

def est_text(cu):
    cl, rel = EST[cu]
    return THEME + 'classDiagram\n  direction LR\n' + '\n'.join('  ' + l for n in cl for l in clase(n).split('\n')) + '\n' + '\n'.join('  ' + r for r in rel)

def din_text(cu):
    return THEME + DIN[cu]
