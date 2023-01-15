import time
from typing import List, Tuple, Callable

from loguru import logger

from pysjtu import Session, Client
from pysjtu.exceptions import *
from pysjtu.models import SelectionClass

# create .session file if not exist
open(".session", "a").close()

logger.info("Logging in...")
with open(".session", "rb+") as f:
    with Session("LightQuantum", "a_a6rF*D-PVRvkZupEP2", session_file=f) as s:
        client = Client(s)
        # client = pysjtu.create_client("LightQuantum", "a_a6rF*D-PVRvkZupEP2")

        wishlist: List[Tuple[str, Callable[[SelectionClass], bool]]] = [
            ("主修", lambda x: "PHY1253" in x.class_name and "刘世勇" in map(lambda y: y[0], x.teachers)),  # 物理二选一
            ("主修", lambda x: "PHY1253" in x.class_name and "王先智" in map(lambda y: y[0], x.teachers)),
            ("主修", lambda x: "CS2305" in x.class_name and "邓倩妮" in map(lambda y: y[0], x.teachers)),  # 系统结构
            ("交叉", lambda x: "ICE2302" in x.class_name and "陈立" in map(lambda y: y[0], x.teachers)),  # 机器学习
            ("交叉", lambda x: "JCCX0013" in x.class_name),  # 无人驾驶
            ("交叉", lambda x: "PUM2317" in x.class_name and "杜江勤" in map(lambda y: y[0], x.teachers))  # 无人驾驶
            # ("通识", lambda x: "MA911" in x.class_name)
            # ("主修", "CS2303-2"),
            # ("主修", "CS2304-1"),
            # ("主修", "CS2308-3"),
            # ("主修", "MARX1203-12"),
            # ("交叉", "NIS2328-1")
        ]

        logger.info("Getting course list...")
        while True:
            try:
                sectors = client.course_selection_sectors
                break
            except SelectionNotAvailableException:
                logger.info("Selection not available, retrying...")
                time.sleep(0.5)
                continue
        selected = []
        for info in wishlist:
            logger.info(f"querying class satisfying constraint {info}")
            (sector_name, class_filter) = info
            target_sectors = [sector for sector in sectors if sector_name in sector.name]
            if len(target_sectors) == 0:
                logger.warning(f"no sector found for {info}")
                continue
            target_sector = target_sectors[0]
            klass = [klass for klass in target_sector.classes if class_filter(klass)]
            selected.extend(klass)

        logger.info(f"ready to elect {selected}")

        while len(selected) > 0:
            time.sleep(1)
            new_selected = []
            for klass in selected:
                try:
                    klass.register()
                    logger.info(f"Completed - {klass}")
                except FullCapacityException:
                    logger.warning(f"FullCapacity - {klass}")
                    new_selected.append(klass)
                except Exception as e:
                    logger.error(f"Exception: {e} - {klass}")
                    new_selected.append(klass)
            selected = new_selected
