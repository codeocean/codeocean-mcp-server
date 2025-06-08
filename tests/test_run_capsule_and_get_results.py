from bedrock_call import call_bedrock
from mcp_client import get_tools

tools = get_tools()

def assert_search_capsules_used(response):
    """Assert that the run_capsule_and_return_result tool was used in the response."""
    tool_use = response["output"]["message"]["content"][-1]["toolUse"]
    assert tool_use["name"] == "run_capsule_and_return_result", \
        "Expected tool 'run_capsule_and_return_result' to be used"
    assert "run_params" in tool_use["input"], f"Expected 'run_params' in tool input: {tool_use['input']}"
    return tool_use

def test_run_capsule_and_get_results_with_capsule_id():
    """Test running a capsule and getting results using a capsule ID."""
    response = call_bedrock(
        "Run the capsule with ID '12345-abhgc-ddssdd' and return the results.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "12345-abhgc-ddssdd", "Expected capsule_id to be '12345'"

def test_run_capsule_with_pipeline_id():
    """Test running a computation using a pipeline ID instead of capsule ID."""
    response = call_bedrock(
        "Execute the computational pipeline with identifier 'pipeline-567890-xyz' "
        "and provide me with the generated output files.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["pipeline_id"] == "pipeline-567890-xyz", "Expected pipeline_id to be set"
    assert "capsule_id" not in tool_use["input"]["run_params"] or tool_use["input"]["run_params"]["capsule_id"] is None

def test_run_capsule_with_specific_version():
    """Test running a specific version of a capsule."""
    response = call_bedrock(
        "Please run version 3 of capsule 'abc123-def456' and return the computational results for analysis.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "abc123-def456", "Expected capsule_id to be set"
    assert tool_use["input"]["run_params"]["version"] == 3, "Expected version to be 3"

def test_run_capsule_with_data_assets():
    """Test running a capsule with attached data assets."""
    response = call_bedrock(
        "Run capsule 'data-analysis-789' with the genomics dataset 'dataset-001' "
        "mounted at '/data/input' and the reference genome 'refgen-hg38' mounted at '/references'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "data-analysis-789", "Expected capsule_id to be set"
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    assert len(data_assets) == 2, "Expected 2 data assets"
    assert any(da["id"] == "dataset-001" and da["mount"] == "/data/input" for da in data_assets)
    assert any(da["id"] == "refgen-hg38" and da["mount"] == "/references" for da in data_assets)

def test_run_capsule_with_positional_parameters():
    """Test running a capsule with positional command line parameters."""
    response = call_bedrock(
        "Run capsule 'ml-training-456' with the arguments '--epochs 100', '--batch-size 32', "
        "and '--learning-rate 0.001'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "ml-training-456", "Expected capsule_id to be set"
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--epochs" in parameters and "100" in parameters, "Expected epochs parameter"
    assert "--batch-size" in parameters and "32" in parameters, "Expected batch-size parameter"
    assert "--learning-rate" in parameters and "0.001" in parameters, "Expected learning-rate parameter"

def test_run_capsule_with_named_parameters():
    """Test running a capsule with named parameters."""
    response = call_bedrock(
        "Run the bioinformatics capsule 'seq-align-999' with the parameter 'algorithm' set to "
        "'bwa-mem', 'threads' set to '8', and 'output_format' set to 'sam'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "seq-align-999", "Expected capsule_id to be set"
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    assert len(named_params) == 3, "Expected 3 named parameters"
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["algorithm"] == "bwa-mem", "Expected algorithm parameter"
    assert param_dict["threads"] == "8", "Expected threads parameter"
    assert param_dict["output_format"] == "sam", "Expected output_format parameter"

def test_run_capsule_with_complex_data_processing():
    """Test running a capsule with multiple data assets and complex parameters."""
    response = call_bedrock(
        "Execute the advanced image processing capsule 'img-proc-2024' version 2 with the raw "
        "images dataset 'raw-imgs-001' mounted at '/input/images', the calibration data "
        "'calib-data-v3' at '/input/calibration', using parameters 'noise_reduction' set to "
        "'adaptive', 'enhancement_level' set to 'high', and the positional arguments '--parallel' "
        "and '--verbose'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "img-proc-2024", "Expected capsule_id to be set"
    assert tool_use["input"]["run_params"]["version"] == 2, "Expected version 2"
    # Check data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    assert len(data_assets) == 2, "Expected 2 data assets"
    assert any(da["id"] == "raw-imgs-001" and da["mount"] == "/input/images" for da in data_assets)
    assert any(da["id"] == "calib-data-v3" and da["mount"] == "/input/calibration" for da in data_assets)
    # Check named parameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["noise_reduction"] == "adaptive", "Expected noise_reduction parameter"
    assert param_dict["enhancement_level"] == "high", "Expected enhancement_level parameter"
    # Check positional parameters
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--parallel" in parameters, "Expected --parallel parameter"
    assert "--verbose" in parameters, "Expected --verbose parameter"

def test_resume_computation():
    """Test resuming a previously started computation."""
    response = call_bedrock(
        "Resume the computation with ID 'comp-12345-abcdef' that was previously interrupted.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["resume_run_id"] == "comp-12345-abcdef", "Expected resume_run_id to be set"

def test_run_pipeline_with_processes():
    """Test running a pipeline with specific process configurations."""
    response = call_bedrock(
        "Execute pipeline 'data-pipeline-v5' with the preprocessing process using parameters "
        "'clean' set to 'true' and 'normalize' set to 'z-score', and the analysis process with "
        "the positional argument '--fast-mode'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["pipeline_id"] == "data-pipeline-v5", "Expected pipeline_id to be set"
    processes = tool_use["input"]["run_params"]["processes"]
    assert len(processes) >= 2, "Expected at least 2 processes"
    # Find preprocessing process
    preprocess = next((p for p in processes if "preprocess" in p["name"].lower()), None)
    assert preprocess is not None, "Expected preprocessing process"
    preprocess_params = {p["param_name"]: p["value"] for p in preprocess["named_parameters"]}
    assert preprocess_params["clean"] == "true", "Expected clean parameter"
    assert preprocess_params["normalize"] == "z-score", "Expected normalize parameter"
    # Find analysis process
    analysis = next((p for p in processes if "analysis" in p["name"].lower()), None)
    assert analysis is not None, "Expected analysis process"
    assert "--fast-mode" in analysis["parameters"], "Expected --fast-mode parameter"

def test_run_genomics_analysis_workflow():
    """Test running a comprehensive genomics analysis workflow."""
    response = call_bedrock(
        "Run the genomics analysis capsule 'genome-seq-v2.1' version 4 with the patient samples "
        "dataset 'samples-cohort-a' mounted at '/data/samples', reference genome 'hg38-latest' "
        "at '/ref/genome', and variant database 'dbsnp-155' at '/ref/variants'. Use named "
        "parameters 'quality_threshold' set to '30', 'coverage_min' set to '10x', and "
        "'variant_caller' set to 'gatk'. Also include the positional arguments '--joint-calling' "
        "and '--output-vcf'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    # Verify capsule and version
    assert tool_use["input"]["run_params"]["capsule_id"] == "genome-seq-v2.1", "Expected capsule_id to be set"
    assert tool_use["input"]["run_params"]["version"] == 4, "Expected version 4"
    # Verify data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    assert len(data_assets) == 3, "Expected 3 data assets"
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["samples-cohort-a"] == "/data/samples", "Expected samples dataset"
    assert asset_map["hg38-latest"] == "/ref/genome", "Expected reference genome"
    assert asset_map["dbsnp-155"] == "/ref/variants", "Expected variant database"
    # Verify named parameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["quality_threshold"] == "30", "Expected quality_threshold"
    assert param_dict["coverage_min"] == "10x", "Expected coverage_min"
    assert param_dict["variant_caller"] == "gatk", "Expected variant_caller"
    # Verify positional parameters
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--joint-calling" in parameters, "Expected --joint-calling"
    assert "--output-vcf" in parameters, "Expected --output-vcf"

def test_run_machine_learning_training():
    """Test running a machine learning training capsule with hyperparameters."""
    response = call_bedrock(
        "Execute the deep learning training capsule 'pytorch-cnn-v3' with the training dataset "
        "'imagenet-subset' mounted at '/data/train', validation set 'validation-split' at "
        "'/data/val', using hyperparameters 'learning_rate' set to '0.0001', 'batch_size' set to "
        "'64', 'epochs' set to '200', and 'optimizer' set to 'adam'. Include the arguments "
        "'--gpu' and '--tensorboard'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "pytorch-cnn-v3", "Expected capsule_id"
    # Check data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["imagenet-subset"] == "/data/train", "Expected training dataset"
    assert asset_map["validation-split"] == "/data/val", "Expected validation dataset"
    # Check hyperparameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["learning_rate"] == "0.0001", "Expected learning_rate"
    assert param_dict["batch_size"] == "64", "Expected batch_size"
    assert param_dict["epochs"] == "200", "Expected epochs"
    assert param_dict["optimizer"] == "adam", "Expected optimizer"
    # Check positional arguments
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--gpu" in parameters, "Expected --gpu"
    assert "--tensorboard" in parameters, "Expected --tensorboard"

def test_run_climate_simulation():
    """Test running a climate modeling simulation with complex configuration."""
    response = call_bedrock(
        "Run the climate simulation capsule 'climate-model-v6' version 2 with historical "
        "temperature data 'temp-1900-2020' mounted at '/input/temperature', precipitation data "
        "'precip-global' at '/input/precipitation', and topography 'topo-high-res' at "
        "'/input/topography. Configure the simulation with 'start_year' set to '2000', "
        "'end_year' set to '2050', 'resolution' set to '1km', 'scenario' set to 'rcp85', and "
        "include the options '--parallel-processing' and '--detailed-output'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "climate-model-v6", "Expected capsule_id"
    assert tool_use["input"]["run_params"]["version"] == 2, "Expected version 2"
    # Check data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    assert len(data_assets) == 3, "Expected 3 data assets"
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["temp-1900-2020"] == "/input/temperature", "Expected temperature data"
    assert asset_map["precip-global"] == "/input/precipitation", "Expected precipitation data"
    assert asset_map["topo-high-res"] == "/input/topography", "Expected topography data"
    # Check simulation parameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["start_year"] == "2000", "Expected start_year"
    assert param_dict["end_year"] == "2050", "Expected end_year"
    assert param_dict["resolution"] == "1km", "Expected resolution"
    assert param_dict["scenario"] == "rcp85", "Expected scenario"
    # Check options
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--parallel-processing" in parameters, "Expected --parallel-processing"
    assert "--detailed-output" in parameters, "Expected --detailed-output"

def test_run_financial_risk_analysis():
    """Test running a financial risk analysis with market data."""
    response = call_bedrock(
        "Execute the quantitative finance capsule 'risk-analytics-pro' with market data "
        "'sp500-daily' mounted at '/data/equities', bond data 'treasury-yields' at '/data/bonds', "
        "and options data 'options-chain' at '/data/derivatives. Set analysis parameters "
        "'confidence_level' to '0.95', 'time_horizon' to '252', 'simulation_runs' to '10000', "
        "and 'model_type' to 'monte_carlo'. Add the flags '--var-calculation' and "
        "'--stress-testing'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "risk-analytics-pro", "Expected capsule_id"
    # Check financial data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["sp500-daily"] == "/data/equities", "Expected equity data"
    assert asset_map["treasury-yields"] == "/data/bonds", "Expected bond data"
    assert asset_map["options-chain"] == "/data/derivatives", "Expected options data"
    # Check analysis parameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["confidence_level"] == "0.95", "Expected confidence_level"
    assert param_dict["time_horizon"] == "252", "Expected time_horizon"
    assert param_dict["simulation_runs"] == "10000", "Expected simulation_runs"
    assert param_dict["model_type"] == "monte_carlo", "Expected model_type"
    # Check analysis flags
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--var-calculation" in parameters, "Expected --var-calculation"
    assert "--stress-testing" in parameters, "Expected --stress-testing"

def test_run_drug_discovery_pipeline():
    """Test running a comprehensive drug discovery computational pipeline."""
    response = call_bedrock(
        "Run the pharmaceutical research pipeline 'drug-discovery-ai' version 3 with the compound "
        "library 'chembl-v30' mounted at '/data/compounds', protein structures 'pdb-structures' "
        "at '/data/proteins', and binding affinity data 'binding-db' at '/data/affinities. "
        "Configure the pipeline with molecular docking process using 'docking_software' set to "
        "'autodock_vina', 'grid_spacing' set to '0.375', and ADMET prediction process with "
        "'prediction_model' set to 'deepchem' and 'endpoints' set to 'all'. Include the "
        "computational flags '--high-throughput' and '--ensemble-docking'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["pipeline_id"] == "drug-discovery-ai", "Expected pipeline_id"
    assert tool_use["input"]["run_params"]["version"] == 3, "Expected version 3"
    # Check pharmaceutical data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["chembl-v30"] == "/data/compounds", "Expected compound library"
    assert asset_map["pdb-structures"] == "/data/proteins", "Expected protein structures"
    assert asset_map["binding-db"] == "/data/affinities", "Expected binding data"
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--high-throughput" in parameters, "Expected --high-throughput"
    assert "--ensemble-docking" in parameters, "Expected --ensemble-docking"

def test_run_astronomical_data_analysis():
    """Test running an astronomical survey data analysis with telescope observations."""
    response = call_bedrock(
        "Execute the astronomy capsule 'stellar-photometry-v4' with telescope observations "
        "'hubble-survey-2023' mounted at '/obs/optical', infrared data 'spitzer-catalog' at "
        "'/obs/infrared', and star catalog 'gaia-dr3' at '/ref/catalog. Process with photometric "
        "parameters 'aperture_radius' set to '3.0', 'sky_annulus' set to '5.0', 'magnitude_limit' "
        "set to '25.0', and 'filter_set' set to 'UBVRI'. Use the processing options "
        "'--cosmic-ray-removal' and '--astrometric-correction'.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "stellar-photometry-v4", "Expected capsule_id"
    # Check astronomical data assets
    data_assets = tool_use["input"]["run_params"]["data_assets"]
    asset_map = {da["id"]: da["mount"] for da in data_assets}
    assert asset_map["hubble-survey-2023"] == "/obs/optical", "Expected optical observations"
    assert asset_map["spitzer-catalog"] == "/obs/infrared", "Expected infrared data"
    assert asset_map["gaia-dr3"] == "/ref/catalog", "Expected star catalog"
    # Check photometric parameters
    named_params = tool_use["input"]["run_params"]["named_parameters"]
    param_dict = {p["param_name"]: p["value"] for p in named_params}
    assert param_dict["aperture_radius"] == "3.0", "Expected aperture_radius"
    assert param_dict["sky_annulus"] == "5.0", "Expected sky_annulus"
    assert param_dict["magnitude_limit"] == "25.0", "Expected magnitude_limit"
    assert param_dict["filter_set"] == "UBVRI", "Expected filter_set"
    # Check processing options
    parameters = tool_use["input"]["run_params"]["parameters"]
    assert "--cosmic-ray-removal" in parameters, "Expected --cosmic-ray-removal"
    assert "--astrometric-correction" in parameters, "Expected --astrometric-correction"
