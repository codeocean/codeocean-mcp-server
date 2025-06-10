import pytest
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

# ──────────────────────────────────────────────
# Define all test cases here: (prompt, expected_run_params)
# ──────────────────────────────────────────────
test_cases = [
    # 1) capsule_id only
    (
        "Run the capsule with ID '12345-abhgc-ddssdd' and return the results.",
        {"capsule_id": "12345-abhgc-ddssdd"},
    ),
    # 2) pipeline_id only
    (
        "Execute the computational pipeline with identifier 'pipeline-567890-xyz' "
        "and provide me with the generated output files.",
        {"pipeline_id": "pipeline-567890-xyz", "capsule_id": None},
    ),
    # 3) capsule_id + version
    (
        "Please run version 3 of capsule 'abc123-def456' and return the computational results for analysis.",
        {"capsule_id": "abc123-def456", "version": 3},
    ),
    # 4) data_assets only
    (
        "Run capsule'1234-9876-43456-659' and get the results, with the genomics dataset 'dataset-001' "
        "mounted at '/data/input' and the reference genome 'refgen-hg38' mounted at '/references'.",
        {
            "capsule_id": "1234-9876-43456-659",
            "data_assets": [
                {"id": "dataset-001",  "mount": "/data/input"},
                {"id": "refgen-hg38",   "mount": "/references"},
            ],
        },
    ),
    # 5) positional parameters
    (
        "Run capsule '1234-9876-43456-654' with the arguments '--epochs 100', '--batch-size 32', "
        "and '--learning-rate 0.001', and then get the results.",
        {
            "capsule_id": "1234-9876-43456-654",
            "parameters": ["--epochs", "100", "--batch-size", "32", "--learning-rate", "0.001"],
        },
    ),
    # 6) named parameters
    (
        "Run the bioinformatics capsule 'seq-align-999' with the parameter 'algorithm' set to "
        "'bwa-mem', 'threads' set to '8', and 'output_format' set to 'sam'.",
        {
            "capsule_id": "seq-align-999",
            "named_parameters": {
                "algorithm":     "bwa-mem",
                "threads":       "8",
                "output_format": "sam",
            },
        },
    ),
    # 7) complex data + named + positional
    (
        "Execute the advanced image processing capsule 'img-proc-2024' version 2 with the raw "
        "images dataset 'raw-imgs-001' mounted at '/input/images', the calibration data "
        "'calib-data-v3' at '/input/calibration', using parameters 'noise_reduction' set to "
        "'adaptive', 'enhancement_level' set to 'high', and the positional arguments '--parallel' "
        "and '--verbose'.",
        {
            "capsule_id": "img-proc-2024",
            "version":    2,
            "data_assets": [
                {"id": "raw-imgs-001",  "mount": "/input/images"},
                {"id": "calib-data-v3", "mount": "/input/calibration"},
            ],
            "named_parameters": {
                "noise_reduction":   "adaptive",
                "enhancement_level": "high",
            },
            "parameters": ["--parallel", "--verbose"],
        },
    ),
    # 9) pipeline with processes
    (
        "Execute pipeline 'data-pipeline-v5' with the preprocessing process using parameters "
        "'clean' set to 'true' and 'normalize' set to 'z-score', and the analysis process with "
        "the positional argument '--fast-mode'.",
        {
            "pipeline_id": "data-pipeline-v5",
            "processes": [
                {
                    "name_contains":       "preprocess",
                    "named_parameters":    {"clean": "true", "normalize": "z-score"},
                },
                {
                    "name_contains":        "analysis",
                    "parameters_contains":  ["--fast-mode"],
                },
            ],
        },
    ),
    # 10) genomics analysis workflow
    (
        "Run the genomics analysis capsule 'genome-seq-v2.1' version 4 with the patient samples "
        "dataset 'samples-cohort-a' mounted at '/data/samples', reference genome 'hg38-latest' "
        "at '/ref/genome', and variant database 'dbsnp-155' at '/ref/variants'. Use named "
        "parameters 'quality_threshold' set to '30', 'coverage_min' set to '10x', and "
        "'variant_caller' set to 'gatk'. Also include the positional arguments '--joint-calling' "
        "and '--output-vcf'.",
        {
            "capsule_id": "genome-seq-v2.1",
            "version":     4,
            "data_assets": [
                {"id": "samples-cohort-a", "mount": "/data/samples"},
                {"id": "hg38-latest",      "mount": "/ref/genome"},
                {"id": "dbsnp-155",        "mount": "/ref/variants"},
            ],
            "named_parameters": {
                "quality_threshold": "30",
                "coverage_min":      "10x",
                "variant_caller":    "gatk",
            },
            "parameters": ["--joint-calling", "--output-vcf"],
        },
    ),
    # 11) ML training
    (
        "Execute the deep learning training capsule 'pytorch-cnn-v3' with the training dataset "
        "'imagenet-subset' mounted at '/data/train', validation set 'validation-split' at "
        "'/data/val', using hyperparameters 'learning_rate' set to '0.0001', 'batch_size' set to "
        "'64', 'epochs' set to '200', and 'optimizer' set to 'adam'. Include the arguments "
        "'--gpu' and '--tensorboard'.",
        {
            "capsule_id": "pytorch-cnn-v3",
            "data_assets": [
                {"id": "imagenet-subset",   "mount": "/data/train"},
                {"id": "validation-split",  "mount": "/data/val"},
            ],
            "named_parameters": {
                "learning_rate": "0.0001",
                "batch_size":    "64",
                "epochs":        "200",
                "optimizer":     "adam",
            },
            "parameters": ["--gpu", "--tensorboard"],
        },
    ),
    # 12) climate simulation
    (
        "Run the climate simulation capsule id 'abcd-trrfd-54343-dsdsd' version 2 with historical "
        "temperature data 'temp-1900-2020' mounted at '/input/temperature', precipitation data "
        "'precip-global' at '/input/precipitation', and topography 'topo-high-res' at "
        "'/input/topography'. Configure the simulation with 'start_year' set to '2000', "
        "'end_year' set to '2050', 'resolution' set to '1km', 'scenario' set to 'rcp85', and "
        "include the options '--parallel-processing' and '--detailed-output'.",
        {
            "capsule_id": "abcd-trrfd-54343-dsdsd",
            "version":     2,
            "data_assets": [
                {"id": "temp-1900-2020",     "mount": "/input/temperature"},
                {"id": "precip-global",      "mount": "/input/precipitation"},
                {"id": "topo-high-res",      "mount": "/input/topography"},
            ],
            "named_parameters": {
                "start_year": "2000",
                "end_year":   "2050",
                "resolution": "1km",
                "scenario":   "rcp85",
            },
            "parameters": ["--parallel-processing", "--detailed-output"],
        },
    ),
    # 13) financial risk analysis
    (
        "Execute the quantitative finance capsule '12345678' with market data "
        "'sp500-daily' mounted at '/data/equities', bond data 'treasury-yields' at '/data/bonds', "
        "and options data 'options-chain' at '/data/derivatives'. Set analysis parameters "
        "'confidence_level' to '0.95', 'time_horizon' to '252', 'simulation_runs' to '10000', "
        "and 'model_type' to 'monte_carlo'. Add the flags '--var-calculation' and "
        "'--stress-testing'.",
        {
            "capsule_id": "12345678",
            "data_assets": [
                {"id": "sp500-daily",     "mount": "/data/equities"},
                {"id": "treasury-yields", "mount": "/data/bonds"},
                {"id": "options-chain",   "mount": "/data/derivatives"},
            ],
            "named_parameters": {
                "confidence_level": "0.95",
                "time_horizon":     "252",
                "simulation_runs":  "10000",
                "model_type":       "monte_carlo",
            },
            "parameters": ["--var-calculation", "--stress-testing"],
        },
    ),
    # 14) drug discovery pipeline
    (
        "Run pipeline id 'abcd-trrfd-54343-dsdsd' version 3 with the compound "
        "library 'chembl-v30' mounted at '/data/compounds', protein structures 'pdb-structures' "
        "at '/data/proteins'. Include the computational flags '--high-throughput' and '--ensemble-docking'.",
        {
            "pipeline_id": "abcd-trrfd-54343-dsdsd",
            "version":     3,
            "data_assets": [
                {"id": "chembl-v30",     "mount": "/data/compounds"},
                {"id": "pdb-structures", "mount": "/data/proteins"},
            ],
            "parameters": ["--high-throughput", "--ensemble-docking"],
        },
    ),
    # 15) astronomical data analysis
    (
        "Execute the astronomy capsule and get the results for '1234-9876-43456' with telescope observations "
        "'hubble-survey-2023' mounted at '/obs/optical', infrared data 'spitzer-catalog' at "
        "'/obs/infrared', and star catalog 'gaia-dr3' at '/ref/catalog'. Process with photometric "
        "parameters 'aperture_radius' set to '3.0', 'sky_annulus' set to '5.0', 'magnitude_limit' "
        "set to '25.0', and 'filter_set' set to 'UBVRI'. Use the processing options "
        "'--cosmic-ray-removal' and '--astrometric-correction'.",
        {
            "capsule_id": "1234-9876-43456",
            "data_assets": [
                {"id": "hubble-survey-2023", "mount": "/obs/optical"},
                {"id": "spitzer-catalog",    "mount": "/obs/infrared"},
                {"id": "gaia-dr3",            "mount": "/ref/catalog"},
            ],
            "named_parameters": {
                "aperture_radius": "3.0",
                "sky_annulus":     "5.0",
                "magnitude_limit": "25.0",
                "filter_set":      "UBVRI",
            },
            "parameters": ["--cosmic-ray-removal", "--astrometric-correction"],
        },
    ),
]

# Generate succinct ids from index + first few chars
ids = [
    "capsule_only",
    "pipeline_only",
    "capsule_version",
    "data_assets",
    "positional_params",
    "named_params",
    "complex_data+params",
    "pipeline_processes",
    "genomics_workflow",
    "ml_training",
    "climate_sim",
    "financial_risk",
    "drug_discovery",
    "astronomical_analysis",
]

@pytest.mark.parametrize("prompt,expected", test_cases, ids=ids)
def test_bedrock_run(prompt, expected):
    # 1) Call Bedrock
    response = call_bedrock(prompt, tools=tools)
    tool_use = assert_search_capsules_used(response)
    run_params = tool_use["input"]["run_params"]

    # 2) Generic assertions
    for key, want in expected.items():
        if key in {"capsule_id", "pipeline_id", "version", "resume_run_id"}:
            # scalars
            if want is None:
                assert key not in run_params or run_params[key] is None
            else:
                assert run_params[key] == want, f"{key} → expected {want!r}, got {run_params.get(key)!r}"

        elif key == "data_assets":
            assets = run_params.get("data_assets", [])
            assert len(assets) == len(want), f"Expected {len(want)} data_assets, got {len(assets)}"
            for exp_asset in want:
                assert any(
                    a.get("id") == exp_asset["id"] and a.get("mount") == exp_asset["mount"]
                    for a in assets
                ), f"Missing data asset {exp_asset!r}"

        elif key == "parameters":
            params = run_params.get("parameters", [])
            for p in want:
                assert p in params, f"Expected positional parameter {p!r} in {params!r}"

        elif key == "named_parameters":
            named = run_params.get("named_parameters", [])
            param_map = {p["param_name"]: p["value"] for p in named}
            for name, val in want.items():
                assert param_map.get(name) == val, f"{name} → expected {val!r}, got {param_map.get(name)!r}"

        elif key == "processes":
            procs = run_params.get("processes", [])
            for exp in want:
                # find matching process
                proc = next((p for p in procs if exp["name_contains"] in p["name"].lower()), None)
                assert proc, f"No process with name containing {exp['name_contains']!r}"
                # check its named params
                if exp.get("named_parameters"):
                    pm = {p["param_name"]: p["value"] for p in proc["named_parameters"]}
                    for n, v in exp["named_parameters"].items():
                        assert pm.get(n) == v, f"In process '{proc['name']}', {n}→ expected {v!r}, got {pm.get(n)!r}"
                # check its positional params
                if exp.get("parameters_contains"):
                    for p in exp["parameters_contains"]:
                        assert p in proc.get("parameters", []), f"In process '{proc['name']}', missing param {p!r}"

        else:
            pytest.skip(f"Unknown assertion key: {key}")