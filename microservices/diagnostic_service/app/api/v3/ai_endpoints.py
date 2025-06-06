"""
Endpoints da API v3 - Inteligência Artificial
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ...ai.ml_engine import (
    PredictiveAnalyzer,
    AnomalyDetector, 
    PatternRecognizer,
    RecommendationEngine
)
from ...models.ai_models import (
    PredictionRequest,
    PredictionResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    PatternAnalysisRequest,
    PatternAnalysisResponse,
    RecommendationRequest,
    RecommendationResponse,
    MLModelInfo,
    TrainingRequest,
    TrainingResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["Artificial Intelligence"])

# Instâncias dos engines de IA
predictive_analyzer = PredictiveAnalyzer()
anomaly_detector = AnomalyDetector()
pattern_recognizer = PatternRecognizer()
recommendation_engine = RecommendationEngine()

@router.post("/predict", response_model=PredictionResponse)
async def predict_system_behavior(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
) -> PredictionResponse:
    """
    Prediz comportamento futuro do sistema baseado em dados históricos
    """
    try:
        logger.info(f"Iniciando predição para {request.prediction_type}")
        
        # Executar predição
        prediction_result = await predictive_analyzer.predict(
            data=request.historical_data,
            prediction_type=request.prediction_type,
            time_horizon=request.time_horizon,
            confidence_threshold=request.confidence_threshold
        )
        
        # Agendar atualização do modelo em background
        background_tasks.add_task(
            predictive_analyzer.update_model_performance,
            request.prediction_type,
            prediction_result
        )
        
        return PredictionResponse(
            prediction_id=prediction_result["prediction_id"],
            prediction_type=request.prediction_type,
            predicted_values=prediction_result["values"],
            confidence_score=prediction_result["confidence"],
            time_horizon=request.time_horizon,
            risk_factors=prediction_result["risk_factors"],
            recommendations=prediction_result["recommendations"],
            model_version=prediction_result["model_version"],
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_system_anomalies(
    request: AnomalyDetectionRequest
) -> AnomalyDetectionResponse:
    """
    Detecta anomalias em tempo real nos dados do sistema
    """
    try:
        logger.info(f"Detectando anomalias em {len(request.metrics)} métricas")
        
        # Executar detecção de anomalias
        detection_result = await anomaly_detector.detect_anomalies_v3(
            metrics=request.metrics,
            sensitivity=request.sensitivity,
            time_window=request.time_window,
            baseline_period=request.baseline_period
        )
        
        return AnomalyDetectionResponse(
            detection_id=detection_result["detection_id"],
            anomalies_found=detection_result["anomalies"],
            severity_scores=detection_result["severity_scores"],
            affected_components=detection_result["affected_components"],
            root_cause_analysis=detection_result["root_causes"],
            recommended_actions=detection_result["actions"],
            confidence_level=detection_result["confidence"],
            detection_timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção de anomalias: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na detecção: {str(e)}")

@router.post("/analyze-patterns", response_model=PatternAnalysisResponse)
async def analyze_system_patterns(
    request: PatternAnalysisRequest
) -> PatternAnalysisResponse:
    """
    Analisa padrões de comportamento do sistema
    """
    try:
        logger.info(f"Analisando padrões em {request.analysis_period} dias")
        
        # Executar análise de padrões
        pattern_result = await pattern_recognizer.analyze_patterns(
            data=request.system_data,
            analysis_period=request.analysis_period,
            pattern_types=request.pattern_types,
            granularity=request.granularity
        )
        
        return PatternAnalysisResponse(
            analysis_id=pattern_result["analysis_id"],
            identified_patterns=pattern_result["patterns"],
            pattern_strength=pattern_result["strength"],
            seasonal_trends=pattern_result["seasonal"],
            usage_patterns=pattern_result["usage"],
            performance_cycles=pattern_result["cycles"],
            insights=pattern_result["insights"],
            analysis_timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na análise de padrões: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_ai_recommendations(
    request: RecommendationRequest
) -> RecommendationResponse:
    """
    Gera recomendações inteligentes baseadas no estado do sistema
    """
    try:
        logger.info(f"Gerando recomendações para {request.context}")
        
        # Gerar recomendações
        recommendations_result = await recommendation_engine.generate_recommendations_v3(
            system_state=request.system_state,
            user_preferences=request.user_preferences,
            context=request.context,
            priority_level=request.priority_level
        )
        
        return RecommendationResponse(
            recommendation_id=recommendations_result["recommendation_id"],
            recommendations=recommendations_result["recommendations"],
            priority_scores=recommendations_result["priorities"],
            expected_impact=recommendations_result["impact"],
            implementation_difficulty=recommendations_result["difficulty"],
            estimated_time=recommendations_result["time"],
            risk_assessment=recommendations_result["risks"],
            success_probability=recommendations_result["success_rate"],
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na geração de recomendações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro nas recomendações: {str(e)}")

@router.get("/models", response_model=List[MLModelInfo])
async def get_ml_models_info() -> List[MLModelInfo]:
    """
    Retorna informações sobre os modelos de ML disponíveis
    """
    try:
        models_info = []
        
        # Informações do modelo preditivo
        pred_info = await predictive_analyzer.get_model_info()
        models_info.append(MLModelInfo(
            model_id=pred_info["model_id"],
            model_name="Predictive Analyzer",
            model_type="Time Series Forecasting",
            version=pred_info["version"],
            accuracy=pred_info["accuracy"],
            last_trained=pred_info["last_trained"],
            training_data_size=pred_info["data_size"],
            features_count=pred_info["features"],
            status=pred_info["status"]
        ))
        
        # Informações do detector de anomalias
        anom_info = await anomaly_detector.get_model_info()
        models_info.append(MLModelInfo(
            model_id=anom_info["model_id"],
            model_name="Anomaly Detector",
            model_type="Unsupervised Learning",
            version=anom_info["version"],
            accuracy=anom_info["accuracy"],
            last_trained=anom_info["last_trained"],
            training_data_size=anom_info["data_size"],
            features_count=anom_info["features"],
            status=anom_info["status"]
        ))
        
        # Informações do reconhecedor de padrões
        pattern_info = await pattern_recognizer.get_model_info()
        models_info.append(MLModelInfo(
            model_id=pattern_info["model_id"],
            model_name="Pattern Recognizer",
            model_type="Pattern Mining",
            version=pattern_info["version"],
            accuracy=pattern_info["accuracy"],
            last_trained=pattern_info["last_trained"],
            training_data_size=pattern_info["data_size"],
            features_count=pattern_info["features"],
            status=pattern_info["status"]
        ))
        
        return models_info
        
    except Exception as e:
        logger.error(f"Erro ao obter informações dos modelos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/train-model", response_model=TrainingResponse)
async def train_ml_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
) -> TrainingResponse:
    """
    Inicia treinamento de modelo de ML
    """
    try:
        logger.info(f"Iniciando treinamento do modelo {request.model_type}")
        
        # Validar dados de treinamento
        if not request.training_data or len(request.training_data) < 100:
            raise HTTPException(
                status_code=400, 
                detail="Dados de treinamento insuficientes (mínimo 100 amostras)"
            )
        
        # Iniciar treinamento em background
        training_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if request.model_type == "predictive":
            background_tasks.add_task(
                predictive_analyzer.train_model,
                request.training_data,
                request.model_parameters,
                training_id
            )
        elif request.model_type == "anomaly":
            background_tasks.add_task(
                anomaly_detector.train_model,
                request.training_data,
                request.model_parameters,
                training_id
            )
        elif request.model_type == "pattern":
            background_tasks.add_task(
                pattern_recognizer.train_model,
                request.training_data,
                request.model_parameters,
                training_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de modelo não suportado: {request.model_type}"
            )
        
        return TrainingResponse(
            training_id=training_id,
            model_type=request.model_type,
            status="started",
            estimated_duration=request.estimated_duration or 1800,  # 30 min default
            data_size=len(request.training_data),
            started_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {str(e)}")

@router.get("/training-status/{training_id}")
async def get_training_status(training_id: str) -> Dict[str, Any]:
    """
    Verifica status do treinamento de modelo
    """
    try:
        # Verificar status em todos os engines
        status_info = {
            "training_id": training_id,
            "status": "unknown",
            "progress": 0,
            "estimated_remaining": None,
            "current_metrics": {},
            "errors": []
        }
        
        # Verificar no analisador preditivo
        pred_status = await predictive_analyzer.get_training_status(training_id)
        if pred_status:
            status_info.update(pred_status)
            return status_info
        
        # Verificar no detector de anomalias
        anom_status = await anomaly_detector.get_training_status(training_id)
        if anom_status:
            status_info.update(anom_status)
            return status_info
        
        # Verificar no reconhecedor de padrões
        pattern_status = await pattern_recognizer.get_training_status(training_id)
        if pattern_status:
            status_info.update(pattern_status)
            return status_info
        
        raise HTTPException(status_code=404, detail="Training ID não encontrado")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/optimize-models")
async def optimize_ml_models(
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Otimiza todos os modelos de ML
    """
    try:
        logger.info("Iniciando otimização de modelos ML")
        
        # Agendar otimização em background
        background_tasks.add_task(predictive_analyzer.optimize_model)
        background_tasks.add_task(anomaly_detector.optimize_model)
        background_tasks.add_task(pattern_recognizer.optimize_model)
        
        return {
            "message": "Otimização de modelos iniciada",
            "status": "running",
            "estimated_duration": "15-30 minutos"
        }
        
    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/performance-metrics")
async def get_ai_performance_metrics() -> Dict[str, Any]:
    """
    Retorna métricas de performance dos sistemas de IA
    """
    try:
        metrics = {
            "predictive_analyzer": await predictive_analyzer.get_performance_metrics(),
            "anomaly_detector": await anomaly_detector.get_performance_metrics(),
            "pattern_recognizer": await pattern_recognizer.get_performance_metrics(),
            "recommendation_engine": await recommendation_engine.get_performance_metrics(),
            "overall_health": "healthy",
            "last_updated": datetime.now()
        }
        
        # Calcular saúde geral
        avg_accuracy = sum([
            metrics["predictive_analyzer"]["accuracy"],
            metrics["anomaly_detector"]["accuracy"],
            metrics["pattern_recognizer"]["accuracy"]
        ]) / 3
        
        if avg_accuracy > 0.9:
            metrics["overall_health"] = "excellent"
        elif avg_accuracy > 0.8:
            metrics["overall_health"] = "good"
        elif avg_accuracy > 0.7:
            metrics["overall_health"] = "fair"
        else:
            metrics["overall_health"] = "needs_improvement"
        
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.delete("/models/{model_id}")
async def delete_ml_model(model_id: str) -> Dict[str, str]:
    """
    Remove um modelo de ML específico
    """
    try:
        logger.info(f"Removendo modelo {model_id}")
        
        # Tentar remover de cada engine
        removed = False
        
        if await predictive_analyzer.delete_model(model_id):
            removed = True
        elif await anomaly_detector.delete_model(model_id):
            removed = True
        elif await pattern_recognizer.delete_model(model_id):
            removed = True
        
        if not removed:
            raise HTTPException(status_code=404, detail="Modelo não encontrado")
        
        return {
            "message": f"Modelo {model_id} removido com sucesso",
            "status": "deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/export-model/{model_id}")
async def export_ml_model(model_id: str) -> Dict[str, Any]:
    """
    Exporta um modelo de ML para backup ou transferência
    """
    try:
        logger.info(f"Exportando modelo {model_id}")
        
        # Tentar exportar de cada engine
        export_data = None
        
        export_data = await predictive_analyzer.export_model(model_id)
        if not export_data:
            export_data = await anomaly_detector.export_model(model_id)
        if not export_data:
            export_data = await pattern_recognizer.export_model(model_id)
        
        if not export_data:
            raise HTTPException(status_code=404, detail="Modelo não encontrado")
        
        return {
            "model_id": model_id,
            "export_data": export_data,
            "exported_at": datetime.now(),
            "format": "pickle",
            "size_mb": len(str(export_data)) / (1024 * 1024)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/import-model")
async def import_ml_model(
    model_data: Dict[str, Any],
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Importa um modelo de ML previamente exportado
    """
    try:
        logger.info("Importando modelo ML")
        
        model_type = model_data.get("model_type")
        if not model_type:
            raise HTTPException(status_code=400, detail="Tipo de modelo não especificado")
        
        # Importar para o engine apropriado
        import_id = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if model_type == "predictive":
            background_tasks.add_task(
                predictive_analyzer.import_model,
                model_data,
                import_id
            )
        elif model_type == "anomaly":
            background_tasks.add_task(
                anomaly_detector.import_model,
                model_data,
                import_id
            )
        elif model_type == "pattern":
            background_tasks.add_task(
                pattern_recognizer.import_model,
                model_data,
                import_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de modelo não suportado: {model_type}"
            )
        
        return {
            "message": "Importação de modelo iniciada",
            "import_id": import_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")