#!/usr/bin/env python3
"""
Knowledge Ingestion Engine CLI

Command-line interface for ingesting and processing knowledge artifacts.
"""

import argparse
from pathlib import Path
from pipeline import run_pipeline
from store.artifact_store import ArtifactStore
import re
from stages.normalize import normalize
from stages.extract import extract
from stages.context import contextualize
from stages.insight import generate_insight
from stages.validate import validate


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='transcript-engine',
        description='Knowledge Ingestion Engine'
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest a transcript file')
    ingest_parser.add_argument('file_path', help='Path to transcript file')
    ingest_parser.add_argument('--project', required=True, help='Project/run identifier')
    
    # Lineage command
    lineage_parser = subparsers.add_parser('lineage', help='Show artifact lineage')
    lineage_parser.add_argument('artifact_id', help='Artifact ID to trace')
    
    # Replay command
    replay_parser = subparsers.add_parser('replay', help='Replay a stage with new version')
    replay_parser.add_argument('artifact_id', help='Artifact ID to replay from')
    replay_parser.add_argument('--stage', required=True, 
                               choices=['normalize', 'extract', 'contextualize', 'insight', 'validate'],
                               help='Stage to replay')
    
    args = parser.parse_args()
    
    if args.command == 'ingest':
        ingest(args.file_path, args.project)
    elif args.command == 'lineage':
        lineage(args.artifact_id)
    elif args.command == 'replay':
        replay(args.artifact_id, args.stage)


def ingest(file_path: str, run_id: str):
    """
    Ingest a transcript file through the pipeline.
    
    Args:
        file_path: Path to input file
        run_id: Run identifier
    """
    # Read file contents
    path = Path(file_path)
    raw_text = path.read_text()
    
    # Run pipeline
    artifacts = run_pipeline(raw_text, run_id)
    
    # Extract artifacts from dictionary
    transcript = artifacts["transcript"]
    extraction = artifacts["extraction"]
    contextualized = artifacts["contextualized"]
    insight = artifacts["insight"]
    validated = artifacts["validated"]
    
    # Print results
    print()
    print("=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print()
    print(f"Run ID: {run_id}")
    print()
    
    # Confidence evolution with arrows
    print("Confidence Evolution:")
    confidences = [
        ("Normalize", transcript.confidence, None),
        ("Extract", extraction.confidence, transcript.confidence),
        ("Contextualize", contextualized.confidence, extraction.confidence),
        ("Insight", insight.confidence, contextualized.confidence),
        ("Validate", validated.confidence, insight.confidence)
    ]
    
    for stage_name, conf, prev_conf in confidences:
        if prev_conf is None:
            arrow = ""
            print(f"  {stage_name:15} {conf:.2f}")
        else:
            if conf > prev_conf:
                arrow = "↑"
            elif conf < prev_conf:
                arrow = "↓"
            else:
                arrow = "→"
            print(f"  {stage_name:15} {conf:.2f} {arrow}")
    
    print()
    print(f"Final Status: {validated.status}")
    print(f"Hallucination Risk: {validated.content['hallucination_risk']}")
    print(f"Referenced Context: {len(validated.referenced_context)} item(s)")
    print()
    print("=" * 60)
    print("REPLAY THIS STAGE")
    print("=" * 60)
    print()
    print(f"transcript-engine replay <artifact_id> --stage <stage>")
    print()
    print("=" * 60)
    print()


def lineage(artifact_id: str):
    """
    Show artifact lineage and version history.
    
    Args:
        artifact_id: Artifact ID to trace
    """
    store = ArtifactStore()
    
    # Load artifact
    artifact = store.load_artifact(artifact_id)
    
    # Print artifact details
    print()
    print("=" * 60)
    print("ARTIFACT DETAILS")
    print("=" * 60)
    print()
    print(f"Artifact ID: {artifact.artifact_id}")
    print(f"Type: {artifact.type}")
    print(f"Version: {artifact.version}")
    print(f"Confidence: {artifact.confidence:.2f}")
    print(f"Status: {artifact.status}")
    print(f"Referenced Context: {len(artifact.referenced_context)} item(s)")
    if artifact.referenced_context:
        for ctx_id in artifact.referenced_context:
            print(f"  - {ctx_id}")
    
    # Print lineage chain
    print()
    print("=" * 60)
    print("LINEAGE CHAIN")
    print("=" * 60)
    print()
    
    # Print current artifact first
    print(f"{artifact.type} (v{artifact.version}, conf={artifact.confidence:.2f})")
    
    if artifact.derived_from:
        _print_lineage_chain(artifact.derived_from, store, level=1)
    else:
        print("(No parent artifacts)")
    
    # Print version history
    print()
    print("=" * 60)
    print("VERSION HISTORY")
    print("=" * 60)
    print()
    
    # Strip version suffix to get base name
    base_name = re.sub(r'_v\d+$', '', artifact_id)
    versions = store.list_versions(base_name)
    
    if versions:
        print(f"Found {len(versions)} version(s) of {base_name}:")
        for version_id in versions:
            version_artifact = store.load_artifact(version_id)
            print(f"  - {version_id} (v{version_artifact.version}, conf={version_artifact.confidence:.2f})")
    else:
        print("(No versions found)")
    
    print()


def _print_lineage_chain(parent_ids: list, store: ArtifactStore, level: int):
    """
    Recursively print lineage chain.
    
    Args:
        parent_ids: List of parent artifact IDs
        store: Artifact store
        level: Indentation level
    """
    indent = "   " * level
    
    for parent_id in parent_ids:
        parent = store.load_artifact(parent_id)
        print(f"{indent}└─ {parent.type} (v{parent.version}, conf={parent.confidence:.2f})")
        
        if parent.derived_from:
            _print_lineage_chain(parent.derived_from, store, level + 1)


def replay(artifact_id: str, stage_name: str):
    """
    Replay a stage with version incrementing.
    
    Args:
        artifact_id: Artifact ID to replay from
        stage_name: Stage to replay
    """
    store = ArtifactStore()
    
    # Load original artifact
    original = store.load_artifact(artifact_id)
    
    # Extract run_id from artifact_id (format: <type>_<date>_<run_id>_v<version>)
    parts = artifact_id.split('_')
    # Find run_id (everything between date and version)
    run_id = '_'.join(parts[2:-1])  # Skip type, date, and version
    
    # Load input artifact based on stage requirements
    # Each stage expects a specific input type from derived_from
    if stage_name in ['extract', 'contextualize', 'insight', 'validate']:
        # These stages need their parent artifact as input
        if not original.derived_from:
            print(f"Error: Artifact {artifact_id} has no parent (derived_from is empty)")
            print(f"Cannot replay {stage_name} stage without input artifact")
            return
        
        # Load the parent artifact
        parent_id = original.derived_from[0]
        input_artifact = store.load_artifact(parent_id)
    else:
        # normalize stage uses the artifact itself
        input_artifact = original
    
    # Calculate new version and artifact_id
    new_version = original.version + 1
    base_id = re.sub(r'_v\d+$', '', original.artifact_id)
    new_artifact_id = f"{base_id}_v{new_version}"
    
    # Run the appropriate stage with overrides (no mutation)
    if stage_name == 'normalize':
        # Normalize expects raw text
        new_artifact = normalize(
            input_artifact.content['text'], 
            run_id,
            version=new_version,
            derived_from_override=[original.artifact_id],
            artifact_id_override=new_artifact_id
        )
    elif stage_name == 'extract':
        # Extract expects transcript artifact
        new_artifact = extract(
            input_artifact, 
            run_id,
            version=new_version,
            derived_from_override=[original.artifact_id],
            artifact_id_override=new_artifact_id
        )
    elif stage_name == 'contextualize':
        # Contextualize expects extraction artifact
        new_artifact = contextualize(
            input_artifact, 
            run_id,
            version=new_version,
            derived_from_override=[original.artifact_id],
            artifact_id_override=new_artifact_id
        )
    elif stage_name == 'insight':
        # Insight expects contextualized artifact
        new_artifact = generate_insight(
            input_artifact, 
            run_id,
            version=new_version,
            derived_from_override=[original.artifact_id],
            artifact_id_override=new_artifact_id
        )
    elif stage_name == 'validate':
        # Validate expects insight artifact
        new_artifact = validate(
            input_artifact, 
            run_id,
            version=new_version,
            derived_from_override=[original.artifact_id],
            artifact_id_override=new_artifact_id
        )
    
    # Print results
    print()
    print("=" * 60)
    print("REPLAY COMPLETE")
    print("=" * 60)
    print()
    print(f"Original Artifact: {original.artifact_id}")
    print(f"New Artifact: {new_artifact.artifact_id}")
    print(f"Stage: {stage_name}")
    print(f"New Version: {new_artifact.version}")
    print(f"New Confidence: {new_artifact.confidence:.2f}")
    print(f"Stored Path: artifacts/{new_artifact.artifact_id}.json")
    print()
    print("-" * 60)
    print("Lineage Command:")
    print(f"transcript-engine lineage {new_artifact.artifact_id}")
    print("-" * 60)
    print()


if __name__ == '__main__':
    main()
