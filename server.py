#!/usr/bin/env python3
"""Spain Company Intelligence MCP Server — powered by OpenMercantil & BORME."""
import httpx
from mcp.server.fastmcp import FastMCP

BASE = "https://openmercantil.es/api/v1"
BORME_API = "https://www.boe.es/datosabiertos/api/borme/sumario"

mcp = FastMCP(
    "Spain Company Intelligence",
    instructions=(
        "Search 2.8M Spanish companies from the official BORME registry. "
        "Find company profiles, current directors, corporate acts, and person lookups. "
        "All data is public domain (CC BY 4.0) from official Spanish government sources. "
        "Use buscar_empresa first to get the slug, then use other tools with that slug."
    ),
)


def _get(url: str, params: dict = None) -> dict:
    with httpx.Client(timeout=15) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
def buscar_empresa(nombre: str, limite: int = 5) -> dict:
    """Search Spanish companies by name or CIF/NIF tax ID.

    Args:
        nombre: Company name or CIF/NIF (e.g. 'Inditex', 'A28017895')
        limite: Max results (default 5, max 20)
    """
    data = _get(f"{BASE}/search", {"q": nombre, "limit": min(limite, 20)})
    return {
        "total_encontradas": data.get("count", 0),
        "empresas": [
            {
                "nombre": item.get("name"),
                "cif": item.get("cif") or "No disponible",
                "slug": item.get("slug"),
                "total_actos_borme": item.get("acts_count", 0),
                "ultima_actividad": item.get("last_seen"),
            }
            for item in data.get("items", [])
        ],
    }


@mcp.tool()
def perfil_empresa(slug: str) -> dict:
    """Get full company profile: status, type, directors, recent BORME acts and activity timeline.

    Args:
        slug: Company slug from buscar_empresa (e.g. 'inditex-sa')
    """
    data = _get(f"{BASE}/company/{slug}")
    c = data.get("company", {})
    kpis = data.get("kpis", {})

    # Recent BORME events (last 5)
    events = [
        {
            "fecha": e.get("date"),
            "tipo": e.get("type"),
            "provincia": e.get("province"),
            "detalle": e.get("details", "")[:200],
        }
        for e in data.get("events", [])[:5]
    ]

    # Current directors
    directors = [
        {"nombre": o.get("name"), "cargo": o.get("role"), "desde": o.get("since")}
        for o in data.get("officers", {}).get("current", [])[:8]
    ]

    return {
        "nombre": c.get("name"),
        "cif": c.get("cif") or "No disponible",
        "tipo_societario": c.get("company_type"),
        "estado": c.get("status"),
        "capital_social": c.get("capital") or "No disponible",
        "direccion": c.get("address") or "No disponible",
        "web": c.get("website") or "No disponible",
        "trabajadores": c.get("workers") or "No disponible",
        "fecha_constitucion": c.get("date_creation") or "No disponible",
        "total_actos_borme": kpis.get("acts_count"),
        "primera_inscripcion": kpis.get("first_seen"),
        "ultima_inscripcion": kpis.get("last_seen"),
        "tipos_acto_mas_frecuentes": data.get("top_event_types", [])[:5],
        "directivos_actuales": directors,
        "ultimos_actos_borme": events,
        "resumen": data.get("summary_text", ""),
    }


@mcp.tool()
def directivos_empresa(slug: str) -> dict:
    """Get complete list of current and historical directors/officers of a Spanish company.

    Args:
        slug: Company slug (e.g. 'telefonica-sa')
    """
    data = _get(f"{BASE}/company/{slug}/officers")
    return {
        "directivos_actuales": [
            {
                "nombre": o.get("name"),
                "cargo": o.get("role"),
                "desde": o.get("since"),
                "slug_persona": o.get("person_slug"),
            }
            for o in data.get("current", [])
        ],
        "ex_directivos": [
            {
                "nombre": o.get("name"),
                "cargo": o.get("role"),
                "desde": o.get("since"),
                "hasta": o.get("until"),
            }
            for o in data.get("historical", [])[:15]
        ],
    }


@mcp.tool()
def buscar_persona(nombre: str) -> dict:
    """Search for a person in the Spanish company registry (to find their director positions).

    Args:
        nombre: Person's full name (e.g. 'Amancio Ortega')
    """
    data = _get(f"{BASE}/person/search", {"q": nombre})
    return {
        "total": data.get("count", 0),
        "personas": [
            {
                "nombre": p.get("name"),
                "slug": p.get("slug"),
                "empresas_activas": p.get("active_positions", 0),
                "total_empresas_historial": p.get("total_positions", 0),
            }
            for p in data.get("items", [])[:10]
        ],
    }


@mcp.tool()
def perfil_persona(slug: str) -> dict:
    """Get all company positions (current and past) held by a person in the Spanish registry.

    Args:
        slug: Person slug from buscar_persona (e.g. 'amancio-ortega-gaona')
    """
    data = _get(f"{BASE}/person/{slug}")
    return {
        "nombre": data.get("name"),
        "primera_aparicion": data.get("first_seen"),
        "ultima_aparicion": data.get("last_seen"),
        "cargos_actuales": [
            {
                "empresa": pos.get("company"),
                "cif": pos.get("cif", ""),
                "cargo": pos.get("role"),
                "desde": pos.get("since"),
            }
            for pos in data.get("active_positions", [])
        ],
        "cargos_anteriores": [
            {
                "empresa": pos.get("company"),
                "cargo": pos.get("role"),
                "desde": pos.get("since"),
                "hasta": pos.get("until", "en curso"),
            }
            for pos in data.get("inactive_positions", [])[:10]
        ],
    }


@mcp.tool()
def borme_diario(fecha: str) -> dict:
    """Get official BORME daily gazette: all new company acts published on a specific date.
    Shows provinces with inscribed acts, capital changes, director changes, dissolutions, etc.

    Args:
        fecha: Date in YYYYMMDD format (e.g. '20260609')
    """
    r = _get(f"{BORME_API}/{fecha}", None)
    if r.get("status", {}).get("code") != "200":
        return {"error": f"No hay datos BORME para la fecha {fecha}"}

    diario_list = r.get("data", {}).get("sumario", {}).get("diario", [])
    if not diario_list:
        return {"error": "Respuesta vacía del BORME"}

    diario = diario_list[0]
    secciones_raw = diario.get("seccion", [])
    if not isinstance(secciones_raw, list):
        secciones_raw = [secciones_raw]

    secciones = []
    for sec in secciones_raw:
        items = sec.get("item", [])
        if not isinstance(items, list):
            items = [items]
        provincias = [i.get("titulo", "") for i in items if i.get("titulo")]
        if provincias:
            secciones.append({
                "seccion": sec.get("nombre", ""),
                "num_provincias_con_actos": len(provincias),
                "provincias": provincias,
            })

    return {
        "fecha": fecha,
        "numero_borme": diario.get("numero", ""),
        "secciones": secciones,
        "nota": "Consulta el PDF de cada provincia en boe.es/diario_borme para ver los actos concretos",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
