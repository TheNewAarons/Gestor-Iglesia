import subprocess
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

PG_BIN = '/opt/homebrew/opt/postgresql@16/bin'


def _backup_dir() -> Path:
    backup_dir = getattr(settings, 'BACKUP_DIR', Path(settings.BASE_DIR) / 'backups')
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def realizar_backup():
    """Dump PostgreSQL → archivo .sql.gz en backups/. Retiene 30 días."""
    db = settings.DATABASES['default']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = _backup_dir()
    sql_file = backup_dir / f'backup_{timestamp}.sql'
    gz_file = Path(str(sql_file) + '.gz')

    env = os.environ.copy()
    env['PATH'] = f"{PG_BIN}:{env.get('PATH', '')}"
    if db.get('PASSWORD'):
        env['PGPASSWORD'] = db['PASSWORD']

    cmd = [
        f'{PG_BIN}/pg_dump',
        '-h', db.get('HOST', 'localhost'),
        '-p', str(db.get('PORT', 5432)),
        '-U', db.get('USER', ''),
        '-F', 'p',
        '-f', str(sql_file),
        db['NAME'],
    ]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error('pg_dump falló: %s', result.stderr)
            return

        # Comprimir
        subprocess.run(['gzip', str(sql_file)], check=True)

        size_kb = gz_file.stat().st_size // 1024
        logger.info('Backup creado: %s (%d KB)', gz_file.name, size_kb)

        _limpiar_backups_viejos(backup_dir, dias=30)

    except subprocess.TimeoutExpired:
        logger.error('Backup timeout después de 5 minutos.')
    except Exception as exc:
        logger.error('Error en backup: %s', exc)
        if sql_file.exists():
            sql_file.unlink()


def _limpiar_backups_viejos(backup_dir: Path, dias: int):
    limite = datetime.now() - timedelta(days=dias)
    eliminados = 0
    for f in backup_dir.glob('backup_*.sql.gz'):
        if datetime.fromtimestamp(f.stat().st_mtime) < limite:
            f.unlink()
            eliminados += 1
    if eliminados:
        logger.info('Eliminados %d backups con más de %d días.', eliminados, dias)


def listar_backups():
    """Retorna lista de backups existentes con nombre, tamaño y fecha."""
    backup_dir = _backup_dir()
    backups = []
    for f in sorted(backup_dir.glob('backup_*.sql.gz'), reverse=True):
        backups.append({
            'nombre': f.name,
            'size_kb': f.stat().st_size // 1024,
            'fecha': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
        })
    return backups
