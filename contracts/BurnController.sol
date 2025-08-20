interface IERC20 {
  function balanceOf(address) external view returns (uint256);
  function burn(uint256) external;
  function transfer(address, uint256) external returns (bool);
}

contract BurnController {
  address public governor; // multisig / timelock
  address public burnAddress = 0x0000000000000000000000000000000000000369;
  mapping(address => bool) public allowedTokens;

  modifier onlyGovernor() { require(msg.sender == governor); _; }

  function setAllowedToken(address token, bool allow) external onlyGovernor {
    allowedTokens[token] = allow;
  }

  // executor calls this to burn tokens already held by controller
  function burnToken(address token, uint256 amount) external onlyGovernor {
    require(allowedTokens[token], "not allowed");
    // if token supports burn()
    try IERC20(token).burn(amount) {
      // burned via token's burn()
    } catch {
      // fallback: transfer to burnAddress if token cannot burn
      IERC20(token).transfer(burnAddress, amount);
    }
    emit BurnExecuted(token, amount, block.timestamp);
  }

  event BurnExecuted(address indexed token, uint256 amount, uint256 ts);
}
