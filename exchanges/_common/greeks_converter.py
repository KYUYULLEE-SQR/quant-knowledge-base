"""
Greeks Converter: OKX PA/BS and Deribit

Converts Greeks between different units:
- OKX PA (BTC units) ↔ OKX BS (USD units)
- Deribit (USD units) ↔ BTC units

Usage:
    from greeks_converter import GreeksConverter

    converter = GreeksConverter(btc_price=88500.0)

    # Convert OKX PA to USD
    theta_usd = converter.okx_pa_to_usd(theta_pa=-0.001172, greek_type='theta')

    # Convert Deribit to BTC
    theta_btc = converter.deribit_to_btc(theta_deribit=-322.13, greek_type='theta')

Last Updated: 2025-12-23
Source: knowledge/exchanges/greeks_definitions.md
"""

from typing import Literal, Union, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GreekType = Literal['delta', 'gamma', 'theta', 'vega', 'rho']
Exchange = Literal['okx_pa', 'okx_bs', 'deribit']


class GreeksConverter:
    """
    Convert Greeks between different unit systems.

    Supports:
    - OKX PA (BTC units) ↔ USD
    - OKX BS (USD units) ↔ BTC
    - Deribit (USD units) ↔ BTC
    """

    def __init__(self, btc_price: float):
        """
        Initialize converter with current BTC price.

        Args:
            btc_price: Current BTC price in USD
        """
        if btc_price <= 0:
            raise ValueError(f"BTC price must be positive, got {btc_price}")

        self.btc_price = btc_price
        logger.info(f"GreeksConverter initialized with BTC price: ${btc_price:,.2f}")

    def okx_pa_to_usd(self, value: float, greek_type: GreekType) -> float:
        """
        Convert OKX PA Greeks (BTC units) to USD.

        Args:
            value: Greek value in BTC units
            greek_type: Type of Greek ('theta', 'vega', 'delta', 'gamma')

        Returns:
            Greek value in USD

        Raises:
            ValueError: If greek_type is 'gamma' (unit unclear)

        Examples:
            >>> converter = GreeksConverter(btc_price=88500.0)
            >>> converter.okx_pa_to_usd(-0.001172, 'theta')
            -103.722
        """
        if greek_type == 'gamma':
            raise ValueError(
                "OKX PA Gamma unit is unclear. Use OKX BS Gamma instead. "
                "See: knowledge/exchanges/greeks_definitions.md"
            )

        # PA × BTC_price = USD
        usd_value = value * self.btc_price

        logger.debug(
            f"OKX PA → USD: {value:.6f} BTC ({greek_type}) "
            f"× ${self.btc_price:,.2f} = ${usd_value:,.2f}"
        )

        return usd_value

    def okx_pa_to_bs(self, value: float, greek_type: GreekType) -> float:
        """
        Convert OKX PA to OKX BS (equivalent to okx_pa_to_usd).

        Args:
            value: PA Greek value
            greek_type: Type of Greek

        Returns:
            BS Greek value (in USD)
        """
        return self.okx_pa_to_usd(value, greek_type)

    def okx_bs_to_btc(self, value: float, greek_type: GreekType) -> float:
        """
        Convert OKX BS Greeks (USD) to BTC units.

        Args:
            value: Greek value in USD
            greek_type: Type of Greek

        Returns:
            Greek value in BTC units

        Examples:
            >>> converter = GreeksConverter(btc_price=88500.0)
            >>> converter.okx_bs_to_btc(-110.39, 'theta')
            -0.001247
        """
        if greek_type == 'gamma':
            # BS Gamma is dimensionless (delta change per $1)
            # Converting to "BTC units" doesn't make standard sense
            # Return as-is with warning
            logger.warning(
                "BS Gamma is dimensionless (delta/$1). "
                "Returning value unchanged."
            )
            return value

        # USD / BTC_price = BTC
        btc_value = value / self.btc_price

        logger.debug(
            f"OKX BS → BTC: ${value:.2f} ({greek_type}) "
            f"÷ ${self.btc_price:,.2f} = {btc_value:.6f} BTC"
        )

        return btc_value

    def deribit_to_btc(self, value: float, greek_type: GreekType) -> float:
        """
        Convert Deribit Greeks (USD) to BTC units.

        Deribit uses USD Greeks despite being BTC-margined.

        Args:
            value: Deribit Greek value (in USD)
            greek_type: Type of Greek

        Returns:
            Greek value in BTC units

        Examples:
            >>> converter = GreeksConverter(btc_price=88500.0)
            >>> converter.deribit_to_btc(-322.13, 'theta')
            -0.003639
        """
        # Deribit Greeks are in USD, same conversion as OKX BS
        return self.okx_bs_to_btc(value, greek_type)

    def deribit_to_okx_bs(self, value: float, greek_type: GreekType) -> float:
        """
        Compare Deribit to OKX BS (both USD) - no conversion needed.

        Args:
            value: Deribit Greek value
            greek_type: Type of Greek

        Returns:
            Same value (both in USD)
        """
        logger.info(
            f"Deribit and OKX BS both use USD units. "
            f"No conversion needed: {value}"
        )
        return value

    def convert(
        self,
        value: float,
        from_exchange: Exchange,
        to_unit: Literal['usd', 'btc'],
        greek_type: GreekType
    ) -> float:
        """
        General-purpose conversion function.

        Args:
            value: Greek value to convert
            from_exchange: Source exchange ('okx_pa', 'okx_bs', 'deribit')
            to_unit: Target unit ('usd' or 'btc')
            greek_type: Type of Greek

        Returns:
            Converted value

        Examples:
            >>> converter = GreeksConverter(btc_price=88500.0)
            >>> converter.convert(-0.001172, 'okx_pa', 'usd', 'theta')
            -103.722
            >>> converter.convert(-322.13, 'deribit', 'btc', 'theta')
            -0.003639
        """
        # Determine current unit
        if from_exchange == 'okx_pa':
            current_unit = 'btc'
        else:  # okx_bs or deribit
            current_unit = 'usd'

        # No conversion needed
        if current_unit == to_unit:
            logger.info(
                f"{from_exchange} already in {to_unit} units. "
                f"No conversion needed."
            )
            return value

        # Convert
        if current_unit == 'btc' and to_unit == 'usd':
            # BTC → USD (multiply)
            return self.okx_pa_to_usd(value, greek_type)
        elif current_unit == 'usd' and to_unit == 'btc':
            # USD → BTC (divide)
            if from_exchange == 'okx_bs':
                return self.okx_bs_to_btc(value, greek_type)
            else:  # deribit
                return self.deribit_to_btc(value, greek_type)
        else:
            raise ValueError(
                f"Invalid conversion: {from_exchange} ({current_unit}) "
                f"→ {to_unit}"
            )

    def verify_conversion(
        self,
        pa_value: float,
        bs_value: float,
        greek_type: GreekType,
        tolerance: float = 0.10
    ) -> Tuple[bool, float]:
        """
        Verify PA × BTC_price ≈ BS (within tolerance).

        Args:
            pa_value: OKX PA Greek value (BTC)
            bs_value: OKX BS Greek value (USD)
            greek_type: Type of Greek
            tolerance: Acceptable error ratio (default 10%)

        Returns:
            (is_valid, error_ratio)

        Examples:
            >>> converter = GreeksConverter(btc_price=88500.0)
            >>> is_valid, error = converter.verify_conversion(
            ...     pa_value=-0.001172,
            ...     bs_value=-110.39,
            ...     greek_type='theta'
            ... )
            >>> is_valid
            True
            >>> error < 0.10
            True
        """
        if greek_type == 'gamma':
            logger.warning("PA Gamma verification not reliable (unit unclear)")
            return False, float('inf')

        # Convert PA to USD
        pa_as_usd = self.okx_pa_to_usd(pa_value, greek_type)

        # Calculate error
        error_ratio = abs(pa_as_usd - bs_value) / abs(bs_value) if bs_value != 0 else float('inf')

        is_valid = error_ratio <= tolerance

        logger.info(
            f"Conversion verification ({greek_type}):\n"
            f"  PA (BTC): {pa_value:.6f}\n"
            f"  PA → USD: ${pa_as_usd:.2f}\n"
            f"  BS (USD): ${bs_value:.2f}\n"
            f"  Error:    {error_ratio:.2%}\n"
            f"  Valid:    {is_valid} (tolerance: {tolerance:.0%})"
        )

        return is_valid, error_ratio


# Convenience functions
def okx_pa_to_usd(pa_value: float, btc_price: float, greek_type: GreekType) -> float:
    """
    Quick conversion: OKX PA (BTC) → USD.

    Args:
        pa_value: PA Greek value in BTC
        btc_price: Current BTC price
        greek_type: Type of Greek

    Returns:
        USD value
    """
    converter = GreeksConverter(btc_price)
    return converter.okx_pa_to_usd(pa_value, greek_type)


def deribit_to_btc(deribit_value: float, btc_price: float, greek_type: GreekType) -> float:
    """
    Quick conversion: Deribit (USD) → BTC.

    Args:
        deribit_value: Deribit Greek value in USD
        btc_price: Current BTC price
        greek_type: Type of Greek

    Returns:
        BTC value
    """
    converter = GreeksConverter(btc_price)
    return converter.deribit_to_btc(deribit_value, greek_type)


# Example usage
if __name__ == "__main__":
    # Example: Convert OKX PA to USD
    print("=" * 80)
    print("GREEKS CONVERTER EXAMPLES")
    print("=" * 80)
    print()

    btc_price = 88500.0
    converter = GreeksConverter(btc_price)

    # Example 1: OKX PA Theta → USD
    print("Example 1: OKX PA Theta → USD")
    theta_pa = -0.001172  # BTC/day
    theta_usd = converter.okx_pa_to_usd(theta_pa, 'theta')
    print(f"  PA Theta: {theta_pa:.6f} BTC/day")
    print(f"  → USD:    ${theta_usd:.2f}/day")
    print()

    # Example 2: Deribit Theta → BTC
    print("Example 2: Deribit Theta → BTC")
    theta_deribit = -322.13  # USD/day
    theta_btc = converter.deribit_to_btc(theta_deribit, 'theta')
    print(f"  Deribit:  ${theta_deribit:.2f}/day")
    print(f"  → BTC:    {theta_btc:.6f} BTC/day")
    print()

    # Example 3: Verify conversion
    print("Example 3: Verify OKX PA ↔ BS conversion")
    theta_pa = -0.001172
    theta_bs = -110.39
    is_valid, error = converter.verify_conversion(theta_pa, theta_bs, 'theta')
    print(f"  Valid:    {is_valid}")
    print(f"  Error:    {error:.2%}")
    print()

    # Example 4: Batch conversion
    print("Example 4: Portfolio Greeks conversion")
    portfolio_greeks_pa = {
        'theta': -0.0074,  # BTC/day
        'vega': 0.00052,   # BTC per 1% IV
    }

    print("  Portfolio (OKX PA):")
    for greek_name, value in portfolio_greeks_pa.items():
        usd_value = converter.okx_pa_to_usd(value, greek_name)  # type: ignore
        print(f"    {greek_name}: {value:.6f} BTC → ${usd_value:.2f} USD")

    print()
    print("=" * 80)
