"""
Startup validation and diagnostics for the Flashfood Tracker backend.

Validates all critical dependencies and provides comprehensive error reporting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import asyncpg
import redis.asyncio as redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)


class ComponentStatus(str, Enum):
    """Status levels for system components."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StartupStatus:
    """Status information for a system component."""
    component: str
    status: ComponentStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    resolution_steps: Optional[List[str]] = None


@dataclass
class DiagnosticReport:
    """Comprehensive system diagnostic report."""
    timestamp: datetime
    overall_status: ComponentStatus
    components: List[StartupStatus]
    environment_info: Dict[str, str]
    recommendations: List[str]


class StartupValidator:
    """Validates all critical system dependencies during startup."""
    
    def __init__(self):
        self.errors: List[StartupStatus] = []
        self.warnings: List[StartupStatus] = []
        self.successes: List[StartupStatus] = []
    
    async def validate_all(self) -> DiagnosticReport:
        """
        Run all startup validations and return comprehensive report.
        
        Returns:
            DiagnosticReport: Complete system status report
        """
        logger.info("Starting system validation...")
        
        # Run all validations
        await self._validate_database()
        await self._validate_redis()
        self._validate_configuration()
        
        # Generate report
        report = self._generate_report()
        
        # Log summary
        if report.overall_status == ComponentStatus.ERROR:
            logger.error(f"Startup validation failed: {len(self.errors)} errors")
        elif report.overall_status == ComponentStatus.WARNING:
            logger.warning(f"Startup validation completed with warnings: {len(self.warnings)} warnings")
        else:
            logger.info("Startup validation completed successfully")
        
        return report
    
    async def _validate_database(self) -> None:
        """Validate PostgreSQL database connectivity."""
        try:
            # Test connection using asyncpg (faster than SQLAlchemy for connection test)
            conn = await asyncpg.connect(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                timeout=10.0
            )
            
            # Test basic query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            if result == 1:
                self.successes.append(StartupStatus(
                    component="database",
                    status=ComponentStatus.SUCCESS,
                    message="PostgreSQL connection successful",
                    details={
                        "host": settings.POSTGRES_HOST,
                        "port": settings.POSTGRES_PORT,
                        "database": settings.POSTGRES_DB
                    }
                ))
            else:
                raise Exception("Database query returned unexpected result")
                
        except asyncpg.InvalidAuthorizationSpecificationError:
            self.errors.append(StartupStatus(
                component="database",
                status=ComponentStatus.ERROR,
                message="Database authentication failed",
                details={
                    "host": settings.POSTGRES_HOST,
                    "port": settings.POSTGRES_PORT,
                    "user": settings.POSTGRES_USER
                },
                resolution_steps=[
                    "Verify POSTGRES_USER and POSTGRES_PASSWORD are correct",
                    "Check if database user exists and has proper permissions",
                    "Ensure database server is running and accessible"
                ]
            ))
        except asyncpg.InvalidCatalogNameError:
            self.errors.append(StartupStatus(
                component="database",
                status=ComponentStatus.ERROR,
                message=f"Database '{settings.POSTGRES_DB}' does not exist",
                details={"database": settings.POSTGRES_DB},
                resolution_steps=[
                    f"Create database: CREATE DATABASE {settings.POSTGRES_DB};",
                    "Verify POSTGRES_DB environment variable is correct",
                    "Run database migrations if needed"
                ]
            ))
        except (asyncpg.ConnectionError, OSError) as e:
            self.errors.append(StartupStatus(
                component="database",
                status=ComponentStatus.ERROR,
                message="Cannot connect to PostgreSQL server",
                details={
                    "host": settings.POSTGRES_HOST,
                    "port": settings.POSTGRES_PORT,
                    "error": str(e)
                },
                resolution_steps=[
                    "Verify PostgreSQL server is running",
                    "Check network connectivity to database host",
                    "Verify POSTGRES_HOST and POSTGRES_PORT are correct",
                    "Check firewall settings"
                ]
            ))
        except Exception as e:
            self.errors.append(StartupStatus(
                component="database",
                status=ComponentStatus.ERROR,
                message=f"Database validation failed: {str(e)}",
                details={"error": str(e)},
                resolution_steps=[
                    "Check database server logs for errors",
                    "Verify all database environment variables",
                    "Test database connection manually"
                ]
            ))
    
    async def _validate_redis(self) -> None:
        """Validate Redis connectivity."""
        try:
            # Create Redis connection
            redis_client = redis.from_url(
                settings.get_redis_url(),
                socket_timeout=10.0,
                socket_connect_timeout=10.0
            )
            
            # Test connection with ping
            pong = await redis_client.ping()
            
            # Test basic operations
            await redis_client.set("health_check", "ok", ex=60)
            result = await redis_client.get("health_check")
            await redis_client.delete("health_check")
            await redis_client.close()
            
            if pong and result == b"ok":
                self.successes.append(StartupStatus(
                    component="redis",
                    status=ComponentStatus.SUCCESS,
                    message="Redis connection successful",
                    details={
                        "host": settings.REDIS_HOST,
                        "port": settings.REDIS_PORT,
                        "db": settings.REDIS_DB
                    }
                ))
            else:
                raise Exception("Redis operations failed")
                
        except redis.ConnectionError as e:
            # Redis is optional for basic functionality, so this is a warning
            self.warnings.append(StartupStatus(
                component="redis",
                status=ComponentStatus.WARNING,
                message="Cannot connect to Redis server",
                details={
                    "host": settings.REDIS_HOST,
                    "port": settings.REDIS_PORT,
                    "error": str(e)
                },
                resolution_steps=[
                    "Verify Redis server is running",
                    "Check REDIS_HOST and REDIS_PORT configuration",
                    "Application will work without Redis but caching will be disabled"
                ]
            ))
        except Exception as e:
            self.warnings.append(StartupStatus(
                component="redis",
                status=ComponentStatus.WARNING,
                message=f"Redis validation failed: {str(e)}",
                details={"error": str(e)},
                resolution_steps=[
                    "Check Redis server logs",
                    "Verify Redis configuration",
                    "Application will continue without caching"
                ]
            ))
    
    def _validate_configuration(self) -> None:
        """Validate application configuration."""
        # Check for production security settings
        if not settings.DEBUG:  # Production mode
            security_issues = []
            
            if settings.SECRET_KEY == "your-secret-key-here" or len(settings.SECRET_KEY) < 32:
                security_issues.append("SECRET_KEY is weak or default")
            
            if any("localhost" in origin for origin in settings.BACKEND_CORS_ORIGINS):
                security_issues.append("CORS origins include localhost in production")
            
            if security_issues:
                self.warnings.append(StartupStatus(
                    component="security",
                    status=ComponentStatus.WARNING,
                    message="Insecure production configuration detected",
                    details={"issues": security_issues},
                    resolution_steps=[
                        "Generate strong SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
                        "Update CORS origins to production domains only",
                        "Review security checklist for production deployment"
                    ]
                ))
        
        # Validate required configuration
        self.successes.append(StartupStatus(
            component="configuration",
            status=ComponentStatus.SUCCESS,
            message="Configuration validation completed",
            details={
                "cors_origins_count": len(settings.BACKEND_CORS_ORIGINS),
                "debug_mode": settings.DEBUG,
                "api_prefix": settings.API_V1_PREFIX
            }
        ))
    
    def _generate_report(self) -> DiagnosticReport:
        """Generate comprehensive diagnostic report."""
        all_components = self.errors + self.warnings + self.successes
        
        # Determine overall status
        if self.errors:
            overall_status = ComponentStatus.ERROR
        elif self.warnings:
            overall_status = ComponentStatus.WARNING
        else:
            overall_status = ComponentStatus.SUCCESS
        
        # Generate recommendations
        recommendations = []
        if self.errors:
            recommendations.append("Fix all error conditions before proceeding to production")
        if self.warnings:
            recommendations.append("Address warning conditions for optimal performance")
        if overall_status == ComponentStatus.SUCCESS:
            recommendations.append("System is ready for operation")
        
        return DiagnosticReport(
            timestamp=datetime.utcnow(),
            overall_status=overall_status,
            components=all_components,
            environment_info={
                "debug_mode": str(settings.DEBUG),
                "project_name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "api_prefix": settings.API_V1_PREFIX
            },
            recommendations=recommendations
        )


class DiagnosticReporter:
    """Generates diagnostic reports and resolution guidance."""
    
    @staticmethod
    def format_report(report: DiagnosticReport) -> str:
        """Format diagnostic report as human-readable string."""
        lines = [
            f"=== System Diagnostic Report ===",
            f"Timestamp: {report.timestamp.isoformat()}",
            f"Overall Status: {report.overall_status.value.upper()}",
            "",
            "Components:"
        ]
        
        for component in report.components:
            status_icon = {
                ComponentStatus.SUCCESS: "✅",
                ComponentStatus.WARNING: "⚠️",
                ComponentStatus.ERROR: "❌"
            }[component.status]
            
            lines.append(f"  {status_icon} {component.component}: {component.message}")
            
            if component.resolution_steps:
                lines.append("    Resolution steps:")
                for step in component.resolution_steps:
                    lines.append(f"      - {step}")
        
        if report.recommendations:
            lines.extend(["", "Recommendations:"])
            for rec in report.recommendations:
                lines.append(f"  - {rec}")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_dict(report: DiagnosticReport) -> Dict[str, Any]:
        """Convert diagnostic report to dictionary for JSON serialization."""
        return {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status.value,
            "components": [asdict(comp) for comp in report.components],
            "environment_info": report.environment_info,
            "recommendations": report.recommendations
        }


# Global validator instance
startup_validator = StartupValidator()