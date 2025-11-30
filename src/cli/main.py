"""Command-line interface for game telemetry system."""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from telemetry_controller import TelemetryController
from utils.logging import setup_logging


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Game-Agnostic Telemetry System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "command",
        choices=["start", "status"],
        help="Command to execute",
    )
    
    parser.add_argument(
        "--config",
        "-c",
        required=True,
        help="Path to game configuration file (YAML or JSON)",
    )
    
    parser.add_argument(
        "--participant-id",
        "-p",
        help="Participant identifier (will prompt if not provided)",
    )
    
    parser.add_argument(
        "--log-level",
        "-l",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    
    parser.add_argument(
        "--log-file",
        help="Optional log file path",
    )
    
    parser.add_argument(
        "--wait-for-roi",
        action="store_true",
        default=True,
        help="Wait for ROI detection before starting (default: True)",
    )
    
    parser.add_argument(
        "--no-wait-for-roi",
        action="store_false",
        dest="wait_for_roi",
        help="Start immediately without waiting for ROI detection",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=args.log_file,
        log_to_console=True,
    )
    
    # Execute command
    if args.command == "start":
        asyncio.run(start_command(args))
    elif args.command == "status":
        status_command(args)


async def start_command(args):
    """Execute start command."""
    print()
    print("=" * 70)
    print("🎮  게임 텔레메트리 시스템 (Game Telemetry System)")
    print("=" * 70)
    print()
    
    # Prompt for participant ID if not provided
    participant_id = args.participant_id
    if not participant_id:
        print("📝 참가자 정보 입력")
        print("-" * 70)
        while True:
            participant_id = input("참가자 이름 또는 ID를 입력하세요: ").strip()
            if participant_id:
                break
            print("⚠️  참가자 ID는 필수입니다. 다시 입력해주세요.")
            print()
        print()
    
    # Display configuration
    print("⚙️  설정 정보")
    print("-" * 70)
    print(f"   설정 파일: {args.config}")
    print(f"   참가자 ID: {participant_id}")
    if args.wait_for_roi:
        print(f"   ROI 감지: 활성화 (최대 30초 대기)")
    else:
        print(f"   ROI 감지: 비활성화 (즉시 시작)")
    print()
    
    controller = TelemetryController()
    
    try:
        # Load configuration
        config_name = Path(args.config).stem
        print("=" * 70)
        print("📋 1단계: 설정 로드 중...")
        print("-" * 70)
        controller.load_config(args.config)
        print(f"✅ 설정 로드 완료: {config_name}")
        print()
        
        # Wait for ROI and start
        if args.wait_for_roi:
            print("=" * 70)
            print("👀 2단계: 게임 화면 감지 중...")
            print("-" * 70)
            print("   🎮 게임을 실행하고 게임 화면을 띄워주세요")
            print("   ⏱️  최대 30초간 자동으로 감지합니다")
            print("   ℹ️  감지 실패 시에도 녹화는 시작됩니다")
            print()
        else:
            print("=" * 70)
            print("🚀 2단계: 녹화 준비 중...")
            print("-" * 70)
        
        await controller.start(
            participant_id=participant_id,
            wait_for_roi=args.wait_for_roi
        )
        
        # Recording started
        print()
        print("=" * 70)
        print("🔴 3단계: 녹화 진행 중")
        print("-" * 70)
        
        # Check for trigger keys in config
        trigger_info = []
        if hasattr(controller.session_manager, 'config'):
            config = controller.session_manager.config
            if config.session_end_triggers:
                for trigger in config.session_end_triggers:
                    if trigger.type == "keyboard":
                        key = trigger.parameters.get("key", "Unknown")
                        trigger_info.append(f"{key} 키")
                    elif trigger.type == "timeout":
                        timeout = trigger.parameters.get("duration_seconds", 0)
                        trigger_info.append(f"{timeout}초 자동 종료")
        
        print("   🎮 게임을 플레이하세요")
        print()
        print("   종료 방법:")
        if trigger_info:
            for info in trigger_info:
                print(f"      • {info} 누르기")
        print(f"      • Ctrl+C 입력")
        print()
        print("-" * 70)
        print()
        
        # Run until stopped
        await controller.run_until_stopped()
        
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 70)
        print("⏹️  4단계: 녹화 종료 중...")
        print("-" * 70)
        await controller.stop()
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ 오류 발생")
        print("-" * 70)
        print(f"   {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("✅ 녹화 완료!")
    print("-" * 70)
    
    # Show output location
    if hasattr(controller, 'session_manager') and controller.session_manager.session:
        session = controller.session_manager.session
        output_dir = Path(controller.session_manager.config.output_directory) / session.session_id
        print(f"   📂 저장 위치: {output_dir}")
        print(f"   🆔 세션 ID: {session.session_id}")
        
        # Count files
        if output_dir.exists():
            frames = list(output_dir.glob("frame_*.jpg")) + list(output_dir.glob("frame_*.png"))
            print(f"   🖼️  프레임 수: {len(frames)}개")
            
            events_file = output_dir / "events.jsonl"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    event_count = sum(1 for _ in f)
                print(f"   ⌨️  이벤트 수: {event_count}개")
    
    print("=" * 70)
    print()


def status_command(args):
    """Execute status command."""
    # TODO: Implement status checking (requires IPC or state file)
    print("Status command not yet implemented")
    print("Use process monitoring tools to check if telemetry is running")


if __name__ == "__main__":
    main()
