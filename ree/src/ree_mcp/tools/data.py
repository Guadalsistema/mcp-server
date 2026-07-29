"""Generic REData API tool."""

import asyncio
import json
from datetime import datetime
from typing import Literal

from fastmcp import Context
from fastmcp.tools import ToolResult
from pydantic import BaseModel, Field, field_validator, model_validator

from ._common import (
    ReeApiError,
    _normalize_datetime,
    build_data_request,
    fetch_json,
    json_result,
    mcp_log,
)


Category = Literal[
    "balance",
    "demanda",
    "generacion",
    "intercambios",
    "mercados",
    "transporte",
]
TimeTrunc = Literal["hour", "day", "month", "year"]
Language = Literal["es", "en"]
GeoTrunc = Literal["electric_system"]
GeoLimit = Literal["peninsular", "canarias", "baleares", "ceuta", "melilla", "ccaa"]
Widget = Literal[
    "balance-electrico",
    "evolucion",
    "variacion-componentes",
    "variacion-componentes-movil",
    "ire-general",
    "ire-general-anual",
    "ire-general-movil",
    "ire-industria",
    "ire-industria-anual",
    "ire-industria-movil",
    "ire-servicios",
    "ire-servicios-anual",
    "ire-servicios-movil",
    "ire-otras",
    "ire-otras-anual",
    "ire-otras-movil",
    "demanda-maxima-diaria",
    "demanda-maxima-horaria",
    "perdidas-transporte",
    "potencia-maxima-instantanea",
    "variacion-demanda",
    "potencia-maxima-instantanea-variacion",
    "potencia-maxima-instantanea-variacion-historico",
    "variacion-componentes-anual",
    "estructura-generacion",
    "evolucion-renovable-no-renovable",
    "estructura-renovables",
    "estructura-generacion-emisiones-asociadas",
    "evolucion-estructura-generacion-emisiones-asociadas",
    "no-renovables-detalle-emisiones-CO2",
    "maxima-renovable",
    "potencia-instalada",
    "maxima-renovable-historico",
    "maxima-sin-emisiones-historico",
    "francia-frontera",
    "portugal-frontera",
    "marruecos-frontera",
    "andorra-frontera",
    "lineas-francia",
    "lineas-portugal",
    "lineas-marruecos",
    "lineas-andorra",
    "francia-frontera-programado",
    "portugal-frontera-programado",
    "marruecos-frontera-programado",
    "andorra-frontera-programado",
    "enlace-baleares",
    "frontera-fisicos",
    "todas-fronteras-fisicos",
    "frontera-programados",
    "todas-fronteras-programados",
    "energia-no-suministrada-ens",
    "indice-indisponibilidad",
    "tiempo-interrupcion-medio-tim",
    "kilometros-lineas",
    "indice-disponibilidad",
    "numero-cortes",
    "ens-tim",
    "indice-disponibilidad-total",
    "componentes-precio-energia-cierre-desglose",
    "componentes-precio",
    "energia-gestionada-servicios-ajuste",
    "energia-restricciones",
    "precios-restricciones",
    "reserva-potencia-adicional",
    "banda-regulacion-secundaria",
    "energia-precios-regulacion-secundaria",
    "energia-precios-regulacion-terciaria",
    "energia-precios-gestion-desvios",
    "coste-servicios-ajuste",
    "volumen-energia-servicios-ajuste-variacion",
    "precios-mercados-tiempo-real",
    "energia-precios-ponderados-gestion-desvios-before",
    "energia-precios-ponderados-gestion-desvios",
    "energia-precios-ponderados-gestion-desvios-after",
]

WIDGET_CATEGORIES = {
    "balance-electrico": "balance",
    **{
        widget: "demanda"
        for widget in (
            "evolucion",
            "variacion-componentes",
            "variacion-componentes-movil",
            "ire-general",
            "ire-general-anual",
            "ire-general-movil",
            "ire-industria",
            "ire-industria-anual",
            "ire-industria-movil",
            "ire-servicios",
            "ire-servicios-anual",
            "ire-servicios-movil",
            "ire-otras",
            "ire-otras-anual",
            "ire-otras-movil",
        )
    },
    **{
        widget: "generacion"
        for widget in (
            "demanda-maxima-diaria",
            "demanda-maxima-horaria",
            "perdidas-transporte",
            "potencia-maxima-instantanea",
            "variacion-demanda",
            "potencia-maxima-instantanea-variacion",
            "potencia-maxima-instantanea-variacion-historico",
            "variacion-componentes-anual",
            "estructura-generacion",
            "evolucion-renovable-no-renovable",
            "estructura-renovables",
            "estructura-generacion-emisiones-asociadas",
            "evolucion-estructura-generacion-emisiones-asociadas",
            "no-renovables-detalle-emisiones-CO2",
            "maxima-renovable",
            "potencia-instalada",
            "maxima-renovable-historico",
            "maxima-sin-emisiones-historico",
        )
    },
    **{
        widget: "intercambios"
        for widget in (
            "francia-frontera",
            "portugal-frontera",
            "marruecos-frontera",
            "andorra-frontera",
            "lineas-francia",
            "lineas-portugal",
            "lineas-marruecos",
            "lineas-andorra",
            "francia-frontera-programado",
            "portugal-frontera-programado",
            "marruecos-frontera-programado",
            "andorra-frontera-programado",
            "enlace-baleares",
            "frontera-fisicos",
            "todas-fronteras-fisicos",
            "frontera-programados",
            "todas-fronteras-programados",
        )
    },
    **{
        widget: "transporte"
        for widget in (
            "energia-no-suministrada-ens",
            "indice-indisponibilidad",
            "tiempo-interrupcion-medio-tim",
            "kilometros-lineas",
            "indice-disponibilidad",
            "numero-cortes",
            "ens-tim",
            "indice-disponibilidad-total",
        )
    },
    **{
        widget: "mercados"
        for widget in (
            "componentes-precio-energia-cierre-desglose",
            "componentes-precio",
            "energia-gestionada-servicios-ajuste",
            "energia-restricciones",
            "precios-restricciones",
            "reserva-potencia-adicional",
            "banda-regulacion-secundaria",
            "energia-precios-regulacion-secundaria",
            "energia-precios-regulacion-terciaria",
            "energia-precios-gestion-desvios",
            "coste-servicios-ajuste",
            "volumen-energia-servicios-ajuste-variacion",
            "precios-mercados-tiempo-real",
            "energia-precios-ponderados-gestion-desvios-before",
            "energia-precios-ponderados-gestion-desvios",
            "energia-precios-ponderados-gestion-desvios-after",
        )
    },
}


class ReeDataInput(BaseModel):
    """Validated arguments for the REData API tool."""

    category: Category = Field(description="REData API category.")
    widget: Widget = Field(description="Widget slug from the REData API.")
    start_date: str = Field(description="Start date as YYYY-MM-DDTHH:MM.")
    end_date: str = Field(description="End date as YYYY-MM-DDTHH:MM.")
    time_trunc: TimeTrunc = Field(default="day", description="Time aggregation.")
    lang: Language = Field(default="es", description="Response language.")
    geo_trunc: GeoTrunc | None = Field(default=None)
    geo_limit: GeoLimit | None = Field(default=None)
    geo_ids: str | None = Field(
        default=None,
        pattern=r"^\d+$",
        description=(
            "Numeric REE geography ID. For ccaa, Andalucía=6, Aragón=7, "
            "Cantabria=8, Castilla-La Mancha=9, Castilla y León=10, "
            "Cataluña=11, País Vasco=12, Asturias=13, Madrid=16, "
            "Navarra=17, Comunidad Valenciana=18, Extremadura=19, "
            "Galicia=20, La Rioja=23, Murcia=24."
        ),
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def normalize_date(cls, value: str, info) -> str:
        normalized, _ = _normalize_datetime(value, info.field_name)
        return normalized

    @model_validator(mode="after")
    def validate_request(self) -> "ReeDataInput":
        if self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date")

        expected_category = WIDGET_CATEGORIES[self.widget]
        if self.category != expected_category:
            raise ValueError(
                f"widget {self.widget} belongs to category {expected_category}; "
                f"received category {self.category}"
            )

        geography = (self.geo_trunc, self.geo_limit, self.geo_ids)
        if any(value is not None for value in geography) and not all(
            value is not None for value in geography
        ):
            raise ValueError("geo_trunc, geo_limit, and geo_ids must be supplied together")
        return self


def _ree_error_result(request: ReeDataInput, error: ReeApiError) -> ToolResult:
    """Return an MCP tool error without leaking an upstream response body."""
    payload = {
        "error": {
            "source": "REE",
            "code": error.code,
            "message": str(error),
            "retryable": error.retryable,
        },
        "request": request.model_dump(exclude_none=True),
    }
    if error.status_code is not None:
        payload["error"]["status_code"] = error.status_code
    return ToolResult(
        content=json.dumps(payload, indent=2, ensure_ascii=False),
        is_error=True,
    )


async def ree_data(
    request: ReeDataInput,
    ctx: Context | None = None,
) -> str | ToolResult:
    """
    Retrieve a REData widget from Red Electrica's public API.
    """
    url, params = build_data_request(
        request.lang,
        request.category,
        request.widget,
        request.start_date,
        request.end_date,
        request.time_trunc,
        request.geo_trunc,
        request.geo_limit,
        request.geo_ids,
    )
    await mcp_log(
        ctx,
        "Calling the REE REData API",
        extra={"url": url, "params": params},
    )
    try:
        payload = await asyncio.to_thread(fetch_json, url, params)
    except ReeApiError as error:
        await mcp_log(
            ctx,
            "REE REData API call failed",
            level="error",
            extra={
                "url": url,
                "code": error.code,
                "status_code": error.status_code,
                "retryable": error.retryable,
            },
        )
        return _ree_error_result(request, error)

    await mcp_log(
        ctx,
        "REE REData API call completed",
        extra={"url": url, "status": "success"},
    )
    return json_result(
        {
            "source": "REE",
            "service": "REData API",
            "lang": request.lang,
            "category": request.category,
            "widget": request.widget,
            "start_date": params["start_date"],
            "end_date": params["end_date"],
            "time_trunc": request.time_trunc,
            "retrieved_at": datetime.now().isoformat(),
        },
        payload,
    )
