# encoding=utf8
import json
import os

from ape.lib import mysql, setting, oss


def progress(percent: int):
    tid = int(os.getenv("TASK_ID", 0))
    if tid > 0:
        with mysql.get_db_conn() as connection:
            with connection.cursor() as cursor:
                sql = f"UPDATE `sdf_task` SET `progress` = %s, " \
                      f"`updated_at` = REPLACE(unix_timestamp(current_timestamp(3)),'.','') WHERE `id` = %s "
                cursor.execute(sql, (percent, tid,))
                connection.commit()


def complete(tid: int, model_files: str):
    with mysql.get_db_conn() as connection:
        with connection.cursor() as cursor:
            sql = f"UPDATE `sdf_task` SET `model_files` = %s, `progress` = 10000, `status` = 2, `job_status` = 3, " \
                  f"`updated_at` = REPLACE(unix_timestamp(current_timestamp(3)),'.','') WHERE `id` = %s"
            cursor.execute(sql, (model_files, tid,))
            connection.commit()


def upload_model():
    tid = int(os.getenv("TASK_ID", 0))
    run_mode = os.getenv("RUN_MODE", "dev")
    print(tid, run_mode)

    if tid > 0:
        model_oss_path_prefix = f'Download_data/sdf/model/{run_mode}'
        log_oss_path_prefix = f'Download_data/log_sdf/model/{run_mode}'
        settings = setting.Settings()
        model_oss_path = f'{model_oss_path_prefix}/task_{tid}'
        log_oss_path = f'{log_oss_path_prefix}/task_{tid}'

        current_path = os.path.dirname(os.path.abspath(__file__))
        bucket = oss.get_bucket()
        target_bucket = oss.get_bucket(settings.oss_target_bucket_name)
        out_path = os.path.join(os.path.dirname(os.path.dirname(current_path)), "output/mesh")

        # upload mtl
        mtl_path = os.path.join(out_path, "mesh.mtl")
        oss_mtl_path = os.path.join(model_oss_path, "mesh.mtl")
        if os.access(mtl_path, os.F_OK):
            bucket.put_object_from_file(oss_mtl_path, mtl_path)
            target_bucket.put_object_from_file(oss_mtl_path, mtl_path)
            print("upload mtl file succeed.")

        # upload obj
        obj_path = os.path.join(out_path, "mesh.obj")
        oss_obj_path = os.path.join(model_oss_path, "mesh.obj")
        if os.access(obj_path, os.F_OK):
            bucket.put_object_from_file(oss_obj_path, obj_path)
            target_bucket.put_object_from_file(oss_obj_path, obj_path)
            print("upload obj file succeed.")

        # upload ply
        # ply_path = os.path.join(out_path, "model.ply")
        # if os.access(ply_path, os.F_OK):
        #     oss_ply_path = os.path.join(model_oss_path, "model.ply")
        #     bucket.put_object_from_file(oss_ply_path, ply_path)
        #     target_bucket.put_object_from_file(oss_ply_path, ply_path)
        #     print("upload ply file succeed.")

        # upload jpg
        jpg_path = os.path.join(out_path, "albedo.jpg")
        oss_jpg_path = os.path.join(model_oss_path, "albedo.jpg")
        if os.access(jpg_path, os.F_OK):
            bucket.put_object_from_file(oss_jpg_path, jpg_path)
            target_bucket.put_object_from_file(oss_jpg_path, jpg_path)
            print("upload jpg file succeed.")

        # upload log
        log_path = os.path.join(os.path.dirname(os.path.dirname(current_path)), "error.log")
        oss_log_path = os.path.join(log_oss_path, "error.log")
        if os.access(log_path, os.F_OK):
            bucket.put_object_from_file(oss_log_path, log_path)
            target_bucket.put_object_from_file(oss_log_path, log_path)
            print("upload error log file succeed.")

        model_file_dict = {'mtl': oss_mtl_path, 'obj': oss_obj_path, 'jpg': oss_jpg_path, 'ply': ''}
        # complete, update model_files, status, job_status
        complete(tid, json.dumps(model_file_dict))

        print("Upload model Done!")
