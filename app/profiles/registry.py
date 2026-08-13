from app.profiles.base import NetworkProfile
from app.profiles.data import DATA
from app.profiles.dante import DANTE
from app.profiles.aes67 import AES67
from app.profiles.smpte_2110 import SMPTE_2110


PROFILES: dict[str, NetworkProfile] = {
    profile.name: profile
    for profile in [
        DATA,
        DANTE,
        AES67,
        SMPTE_2110,
    ]
}


def get_profile(name: str) -> NetworkProfile:
    try:
        return PROFILES[name]
    except KeyError:
        raise ValueError(f"Unknown network profile: {name}")
