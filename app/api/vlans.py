from fastapi import APIRouter, Depends, Query

from app.dependencies.services import get_vlan_service
from app.schemas.vlan import (
    VlanCreate,
    VlanResponse,
    VlanUpdate,
)
from app.services.vlan import VlanService


router = APIRouter()


@router.get(
    "",
    response_model=list[VlanResponse],
)
def get_vlans(
    site_id: int = Query(..., gt=0),
    service: VlanService = Depends(get_vlan_service),
):
    return service.get_vlans(
        site_id=site_id,
    )

@router.get(
    "/{vid}",
    response_model=VlanResponse,
)
def get_vlan(
    vid: int,
    site_id: int = Query(..., gt=0),
    service: VlanService = Depends(get_vlan_service),
):
    return service.get_vlan(
        vid=vid,
        site_id=site_id,
    )

@router.post(
    "",
    response_model=VlanResponse,
)
def create_vlan(
    data: VlanCreate,
    service: VlanService = Depends(get_vlan_service),
):
    return service.create_vlan(data)


@router.patch(
    "/{vid}",
    response_model=VlanResponse,
)
def update_vlan(
    vid: int,
    data: VlanUpdate,
    service: VlanService = Depends(get_vlan_service),
):
    return service.update_vlan(
        vid=vid,
        data=data,
    )


@router.delete(
    "/{vid}",
)
def delete_vlan(
    vid: int,
    site_id: int = Query(..., gt=0),
    service: VlanService = Depends(get_vlan_service),
):
    service.delete_vlan(
        vid=vid,
        site_id=site_id,
    )

    return {
        "detail": "VLAN deleted successfully.",
    }
