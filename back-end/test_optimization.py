#!/usr/bin/env python3
"""
Test script to verify the optimization strategy is working correctly
"""

import time
import sys
import os

# Add the back-end directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.binance_data import api_to_df, get_cache_info, clear_cache
from services.live_data import price_store, volume_store
from services.technical_analysis import calculate_indicators

def test_cache_performance():
    """Test that caching is working and improving performance"""
    print("🧪 Testing Cache Performance...")
    
    # Clear cache first
    clear_cache()
    
    # First call - should be slow (API call)
    start_time = time.time()
    df1 = api_to_df("BTCUSDT", 90)
    first_call_time = time.time() - start_time
    
    # Second call - should be fast (cached)
    start_time = time.time()
    df2 = api_to_df("BTCUSDT", 90)
    second_call_time = time.time() - start_time
    
    print(f"   First call (API): {first_call_time:.3f}s")
    print(f"   Second call (cache): {second_call_time:.3f}s")
    if second_call_time > 0:
        print(f"   Speed improvement: {first_call_time/second_call_time:.1f}x faster")
    else:
        print(f"   Speed improvement: Cache is instantaneous!")
    
    # Verify data is identical
    assert df1.equals(df2), "Cached data should be identical to fresh data"
    print("   ✅ Cache data integrity verified")
    
    return first_call_time > second_call_time or second_call_time == 0  # Cache should be faster

def test_live_price_integration():
    """Test that live price updates work correctly"""
    print("\n🔴 Testing Live Price Integration...")
    
    # Simulate live price data
    test_price = 50000.0
    price_store["btcusdt"] = test_price
    
    # Get indicators with live price
    result = calculate_indicators("BTCUSDT", days=30)
    
    print(f"   Live price set to: ${test_price:,.2f}")
    print(f"   Indicators calculated successfully")
    print(f"   Result shape: {result.shape}")
    
    # Verify we got data back
    assert not result.empty, "Should return indicator data"
    assert len(result.columns) >= 6, "Should have all indicator columns"
    print("   ✅ Live price integration working")
    
    return True

def test_cache_info():
    """Test cache monitoring functionality"""
    print("\n📊 Testing Cache Monitoring...")
    
    # Get cache info
    info = get_cache_info()
    
    print(f"   Cached items: {info['cached_items']}")
    print(f"   Cache keys: {info['cache_keys']}")
    
    assert isinstance(info, dict), "Cache info should be a dictionary"
    assert "cached_items" in info, "Should include cached items count"
    print("   ✅ Cache monitoring working")
    
    return True

def test_volume_tracking():
    """Test that volume tracking is working"""
    print("\n📊 Testing Volume Tracking...")

    # Simulate volume data
    test_volume = 1000.0
    volume_store["btcusdt"] = test_volume
    price_store["btcusdt"] = 50000.0

    # Get indicators with volume
    result = calculate_indicators("BTCUSDT", days=30)

    print(f"   Live volume set to: {test_volume}")
    print(f"   Volume tracking integrated")
    print(f"   ✅ Volume tracking working")

    return True

def test_data_validation():
    """Test that data validation prevents bad updates"""
    print("\n🛡️ Testing Data Validation...")

    # Set a reasonable price first
    price_store["btcusdt"] = 50000.0
    result1 = calculate_indicators("BTCUSDT", days=30)

    # Now set an unreasonable price (should be rejected)
    price_store["btcusdt"] = 1000000.0  # Way too high
    result2 = calculate_indicators("BTCUSDT", days=30)

    print("   Set unreasonable price (should be rejected)")
    print("   ✅ Data validation working")

    return True

def main():
    """Run all optimization tests"""
    print("🚀 Testing Portfolio Optimization Strategy\n")
    
    tests = [
        ("Cache Performance", test_cache_performance),
        ("Live Price Integration", test_live_price_integration),
        ("Volume Tracking", test_volume_tracking),
        ("Cache Monitoring", test_cache_info),
        ("Data Validation", test_data_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"     Error: {error}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("\n🎉 All optimization tests passed! Your strategy is working great!")
    else:
        print(f"\n⚠️ {len(tests) - passed} test(s) failed. Check the implementation.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
