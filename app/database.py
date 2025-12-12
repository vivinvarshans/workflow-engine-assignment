"""
Database models and operations using SQLAlchemy.
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from typing import Optional
from app.models import ExecutionStatus

# Database setup
DATABASE_URL = "sqlite:///./workflow_engine.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GraphDB(Base):
    """Database model for workflow graphs"""
    __tablename__ = "graphs"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    definition = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class RunDB(Base):
    """Database model for workflow runs"""
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True, index=True)
    graph_id = Column(String, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    initial_state = Column(Text)  # JSON string
    current_state = Column(Text)  # JSON string
    execution_log = Column(Text)  # JSON string (list)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseOperations:
    """Helper class for database operations"""
    
    @staticmethod
    def create_graph(graph_id: str, name: str, definition: dict) -> GraphDB:
        """Create a new graph in the database"""
        db = SessionLocal()
        try:
            graph = GraphDB(
                id=graph_id,
                name=name,
                definition=json.dumps(definition)
            )
            db.add(graph)
            db.commit()
            db.refresh(graph)
            return graph
        finally:
            db.close()
    
    @staticmethod
    def get_graph(graph_id: str) -> Optional[GraphDB]:
        """Retrieve a graph by ID"""
        db = SessionLocal()
        try:
            return db.query(GraphDB).filter(GraphDB.id == graph_id).first()
        finally:
            db.close()
    
    @staticmethod
    def create_run(run_id: str, graph_id: str, initial_state: dict) -> RunDB:
        """Create a new workflow run"""
        db = SessionLocal()
        try:
            run = RunDB(
                id=run_id,
                graph_id=graph_id,
                status=ExecutionStatus.PENDING,
                initial_state=json.dumps(initial_state),
                current_state=json.dumps(initial_state),
                execution_log=json.dumps([])
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            return run
        finally:
            db.close()
    
    @staticmethod
    def get_run(run_id: str) -> Optional[RunDB]:
        """Retrieve a run by ID"""
        db = SessionLocal()
        try:
            return db.query(RunDB).filter(RunDB.id == run_id).first()
        finally:
            db.close()
    
    @staticmethod
    def update_run(
        run_id: str,
        status: Optional[ExecutionStatus] = None,
        current_state: Optional[dict] = None,
        execution_log: Optional[list] = None,
        error: Optional[str] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update a workflow run"""
        db = SessionLocal()
        try:
            run = db.query(RunDB).filter(RunDB.id == run_id).first()
            if run:
                if status:
                    run.status = status
                if current_state is not None:
                    run.current_state = json.dumps(current_state)
                if execution_log is not None:
                    run.execution_log = json.dumps(execution_log)
                if error is not None:
                    run.error = error
                if completed_at is not None:
                    run.completed_at = completed_at
                db.commit()
        finally:
            db.close()
