# 🐔 Sistema de Gestión Avícola — TILCOR S.A.S.

> Trabajo Práctico Integrador — Instancia Evaluativa 2  
> **Carnielli, Matías · Bacari, Fernando**  
> Analistas en Sistemas de Información — IES Córdoba · 2026

---

## 📋 Descripción

Sistema web/PWA para la gestión integral de producción avícola de **TILCOR S.A.S.**, empresa familiar de Córdoba dedicada a la cría de gallinas ponedoras (líneas Lohmann Brown-Classic y LSL-Classic).

Reemplaza cuatro herramientas desconectadas (app Gallinero, planillas en papel, Don Gestión y Excel) por una única plataforma centralizada con alertas automáticas en tiempo real.

**PWA en producción:** https://tilcorvercel.vercel.app

---

## 🚀 Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React.js · PWA (Service Worker) · Modo offline |
| Backend | Django + Django REST Framework |
| Base de datos | PostgreSQL + TimescaleDB (series temporales IoT) |
| IoT / Mensajería | MQTT (Eclipse Mosquitto) + Celery + Redis |
| Infraestructura | Docker · Nginx · SSL · VPS |
| Integraciones | Don Gestión (iframe + REST) · AFIP-WSFE (Zeep SOAP) |
| Deploy | Vercel (frontend) |
| Auth | JWT |

---

## 📦 Módulos del sistema

| ID | Módulo | Estado |
|----|--------|--------|
| M1 | Registro y seguimiento de lotes | 🟡 En desarrollo |
| M2 | Registro diario de producción | 🟡 En desarrollo |
| M3 | Alertas automáticas (viabilidad, mortalidad) | 🟡 En desarrollo |
| M4 | Integración IoT / sensores MQTT | 🟡 En desarrollo |
| M5 | Dashboard ejecutivo | 🟡 En desarrollo |
| M6 | Historial de datos IoT (TimescaleDB) | 🔴 Pendiente |
| M7 | Reportes exportables (PDF/Excel) | 🔴 Pendiente |
| M8 | Integración Don Gestión | 🔴 Pendiente |
| M9 | PWA offline (Service Worker) | 🟡 En desarrollo |
| M10 | AFIP-WSFE (facturación electrónica) | 🔴 Pendiente |
| M11 | Roles y control de acceso | 🟡 En desarrollo |
| M12 | Perfil veterinario (historial clínico) | 🔴 Pendiente |

---

## 👥 Perfiles de usuario

- **Propietario** — Resumen ejecutivo, rentabilidad por lote, AFIP
- **Supervisor** — Dashboard completo, gestión de lotes, alertas
- **Operario** — Registro diario, panel IoT, modo offline
- **Veterinario** — Historial clínico, alertas sanitarias (solo lectura)

---

## 📁 Estructura del repositorio

```
├── frontend/          # React PWA
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   └── public/
├── backend/           # Django + DRF
│   ├── apps/          # Módulos Django
│   └── config/        # Settings, URLs, WSGI
├── docs/              # Documentación del proyecto
│   ├── entregables/   # Documentos TP2
│   └── diagramas/     # Casos de uso, cursogramas
└── .github/           # Templates de issues y workflows
```

---

## 🗺️ Fases del proyecto

| Fase | Contenido | Duración | Estado |
|------|-----------|----------|--------|
| Fase 1 | Análisis, arquitectura, entorno base | 4 semanas | ✅ Completada |
| Fase 2 | UX/UI, prototipo, M1-M2 | 4 semanas | 🟡 En curso |
| Fase 3 | M3 Alertas, M5 Dashboard, M11 Roles | 5 semanas | 🔴 Pendiente |
| Fase 4 | M4/M6 IoT, M7 Reportes, M8 Don Gestión, M10 AFIP | 7 semanas | 🔴 Pendiente |
| Fase 5 | M9/M12 PWA offline, despliegue, documentación | 6 semanas | 🔴 Pendiente |

---

## 📄 Documentación

Los entregables del TP2 están en la carpeta [`docs/entregables/`](./docs/entregables/):

- `B1_Contrato_Alcance_TILCOR.docx` — Contrato de alcance (12 módulos, 5 fases)
- `B5_Manual_Usuario_TILCOR.docx` — Manual de usuario (4 perfiles)
- `B6_Estrategia_Venta_TILCOR.docx` — Estrategia de venta y presupuesto
- `TP2_ParteA_TILCOR.docx` — Análisis del sistema (Parte A)

---

## ⚙️ Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/Mcarnielli/Ingenieria-en-SFT-Tilcor.git
cd Ingenieria-en-SFT-Tilcor

# Frontend
cd frontend
npm install
npm start

# Backend
cd ../backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔗 Links

- **PWA en producción:** https://tilcorvercel.vercel.app
- **Tablero del proyecto:** [GitHub Projects](https://github.com/Mcarnielli/Ingenieria-en-SFT-Tilcor/projects)

---

*IES Córdoba — Analistas en Sistemas de Información — Octubre 2026*
